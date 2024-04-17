import os
import warnings
from io import StringIO

import pandas as pd
import requests
import s3fs
import xarray as xr
import numpy as np

from ._constants import METADATA_TABLE_PATH
from .analyze import (
    simple_forecast as calc_simple_forecast,
    forecast_stats as calc_forecast_stats,
    daily_averages as calc_daily_averages,
    monthly_averages as calc_monthly_averages,
    annual_averages as calc_annual_averages,
)

__all__ = [
    'dates',
    'forecast',
    'forecast_stats',
    'forecast_ensembles',
    'forecast_records',

    'retrospective',
    'daily_averages',
    'monthly_averages',
    'annual_averages',
    'return_periods',

    'metadata_tables',
]

DEFAULT_REST_ENDPOINT = 'https://geoglows.ecmwf.int/api/'
DEFAULT_REST_ENDPOINT_VERSION = 'v2'  # 'v1, v2, latest'
ODP_CORE_S3_BUCKET_URI = 's3://geoglows-v2'
ODP_FORECAST_S3_BUCKET_URI = 's3://geoglows-v2-forecasts'
ODP_RETROSPECTIVE_S3_BUCKET_URI = 's3://geoglows-v2-retrospective'
ODP_S3_BUCKET_REGION = 'us-west-2'


def _forecast_endpoint_decorator(function):
    def from_aws(*args, **kwargs):
        product_name = function.__name__.replace("_", "").lower()
        if product_name == 'forecastrecords':
            warnings.warn('forecast_records are not available from the AWS Open Data Program.')
            return from_rest(*args, **kwargs)

        river_id = kwargs.get('river_id', '')
        river_id = args[0] if len(args) > 0 else river_id

        return_format = kwargs.get('format', 'df')
        assert return_format in ('df', 'xarray'), f'Unsupported return format requested: {return_format}'

        s3 = s3fs.S3FileSystem(anon=True, client_kwargs=dict(region_name=ODP_S3_BUCKET_REGION))
        date = kwargs.get('date', False)
        if not date:
            dates = sorted([x.split('/')[-1] for x in s3.ls(ODP_FORECAST_S3_BUCKET_URI)], reverse=True)
            dates = [x.split('.')[0] for x in dates if x.endswith('.zarr')]  # ignore the index.html file
            dates = [x.replace('00.zarr', '') for x in dates]
            if product_name == 'dates':
                return pd.DataFrame(dict(dates=dates))
            date = dates[0]
        if len(date) == 8:
            date = f'{date}00.zarr'
        elif len(date) == 10:
            date = f'{date}.zarr'
        else:
            raise ValueError('Date must be YYYYMMDD or YYYYMMDDHH format. Use dates() to view available data.')

        s3store = s3fs.S3Map(root=f'{ODP_FORECAST_S3_BUCKET_URI}/{date}', s3=s3, check=False)

        attrs = {
            'source': 'geoglows',
            'forecast_date': date[:8],
            'retrieval_date': pd.Timestamp.now().strftime('%Y%m%d'),
            'units': 'cubic meters per second',
        }
        ds = xr.open_zarr(s3store).sel(rivid=river_id)
        if return_format == 'xarray' and product_name == 'forecastensembles':
            ds = ds.rename({'time': 'datetime', 'rivid': 'river_id'})
            ds.attrs = attrs
            return ds
        df = ds.to_dataframe().round(2).reset_index()

        # rename columns to match the REST API
        if isinstance(river_id, int) or isinstance(river_id, np.int64):
            df = df.pivot(index='time', columns='ensemble', values='Qout')
        else:
            df = df.pivot(index=['time', 'rivid'], columns='ensemble', values='Qout')
            df.index.names = ['time', 'river_id']
        df = df[sorted(df.columns)]
        df.columns = [f'ensemble_{str(x).zfill(2)}' for x in df.columns]

        if product_name == 'forecast':
            df = calc_simple_forecast(df)
        elif product_name == 'forecaststats':
            df = calc_forecast_stats(df)

        if return_format == 'df':
            return df
        ds = df.to_xarray()
        ds.attrs = attrs
        return ds

    def from_rest(*args, **kwargs):
        # update the default values set by the function unless the user has already specified them
        for key, value in function.__kwdefaults__.items() if function.__kwdefaults__ else []:
            if key not in kwargs:
                kwargs[key] = value

        return_format = kwargs.get('format', 'csv')
        assert return_format in ('csv', 'json', 'url'), f'Unsupported format requested: {return_format}'

        # parse out the information necessary to build a request url
        endpoint = kwargs.get('endpoint', DEFAULT_REST_ENDPOINT)
        endpoint = endpoint[:-1] if endpoint[-1] == '/' else endpoint
        endpoint = endpoint + '/api' if not endpoint.endswith('/api') else endpoint
        endpoint = f'https://{endpoint}' if not endpoint.startswith(('https://', 'http://')) else endpoint

        version = kwargs.get('version', DEFAULT_REST_ENDPOINT_VERSION)
        assert version in ('v2', ), ValueError(f'Unrecognized model version parameter: {version}')

        product_name = function.__name__.replace("_", "").lower()

        river_id = args[0] if len(args) > 0 else None
        river_id = kwargs.get('river_id', '') if not river_id else river_id
        if isinstance(river_id, list):
            raise ValueError('Multiple river_ids are not available via REST API or on v1. '
                             'Use data_source="aws" and version="v2" for multiple river_ids.')
        river_id = int(river_id) if river_id else None
        if river_id and version == 'v2':
            assert 1_000_000_000 > river_id >= 110_000_000, ValueError('River ID must be a 9 digit integer')

        # request parameter validation before submitting
        for key in ('endpoint', 'version', 'river_id'):
            if key in kwargs:
                del kwargs[key]
        for key, value in kwargs.items():
            if value is None:
                del kwargs[key]
        for date in ('date', 'start_date', 'end_date'):
            if date in kwargs:
                assert len(str(kwargs[date])) == 8 or len(
                    str(kwargs[date])) == 10, f'Invalid date format: {kwargs[date]}'
        if 'format' in kwargs and kwargs['format'] != 'json':
            del kwargs['format']
        kwargs['source'] = kwargs.get('source', 'pygeoglows')  # allow using default for specific apps which override
        params = '&'.join([f'{key}={value}' for key, value in kwargs.items()])

        # piece together the request url
        request_url = f'{endpoint}/{version}/{product_name}'  # build the base url
        request_url = f'{request_url}/{river_id}' if river_id else request_url  # add the river_id if it exists
        request_url = f'{request_url}?{params}'  # add the query parameters

        if return_format == 'url':
            return request_url.replace(f'source={kwargs["source"]}', '')

        response = requests.get(request_url)

        if response.status_code != 200:
            raise RuntimeError('Received an error from the REST API: ' + response.text)

        if return_format == 'csv':
            df = pd.read_csv(StringIO(response.text))
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
            return df
        elif return_format == 'json':
            return response.json()
        else:
            raise ValueError(f'Unsupported return format requested: {return_format}')

    def main(*args, **kwargs):
        source = kwargs.get('data_source', 'aws')
        assert source in ('rest', 'aws'), ValueError(f'Unrecognized data source requested: {source}')
        if source == 'rest':
            return from_rest(*args, **kwargs)
        return from_aws(*args, **kwargs)
    main.__doc__ = function.__doc__  # necessary for code documentation auto generators
    return main


# Forecast data and derived products
@_forecast_endpoint_decorator
def dates(**kwargs) -> dict or str:
    """
    Gets a list of available forecast product dates

    Keyword Args:
        data_source (str): location to query for data, either 'rest' or 'aws'. default is aws.

    Returns:
        dict or str

        the csv is a single column with a header of 'available_dates' and 1 row per date, sorted oldest to newest
        The dictionary structure is {'available_dates': ['list', 'of', 'dates', 'YYYYMMDD', 'format']}
    """
    pass


@_forecast_endpoint_decorator
def forecast(*, river_id: int, date: str, format: str, data_source: str,
             **kwargs) -> pd.DataFrame or xr.Dataset:
    """
    Gets the average forecasted flow for a certain river_id on a certain date

    Keyword Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        date (str): a string specifying the date to request in YYYYMMDD format, returns the latest available if not specified
        format: if data_source=="rest": csv, json, or url, default csv. if data_source=="aws": df or xarray
        data_source (str): location to query for data, either 'rest' or 'aws'. default is aws.

    Returns:
        pd.DataFrame or dict or str
    """
    pass


@_forecast_endpoint_decorator
def forecast_stats(*, river_id: int, date: str, format: str, data_source: str,
                   **kwargs) -> pd.DataFrame or xr.Dataset:
    """
    Retrieves the min, 25%, mean, median, 75%, and max river discharge of the 51 ensembles members for a river_id
    The 52nd higher resolution member is excluded

    Keyword Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        date (str): a string specifying the date to request in YYYYMMDD format, returns the latest available if not specified
        format (str): if data_source=="rest": csv, json, or url, default csv. if data_source=="aws": df or xarray
        data_source (str): location to query for data, either 'rest' or 'aws'. default is aws.

    Returns:
        pd.DataFrame or dict or str
    """
    pass


@_forecast_endpoint_decorator
def forecast_ensembles(*, river_id: int, date: str, format: str, data_source: str,
                       **kwargs) -> pd.DataFrame or xr.Dataset:
    """
    Retrieves each of 52 time series of forecasted discharge for a river_id on a certain date

    Keyword Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        date (str): a string specifying the date to request in YYYYMMDD format, returns the latest available if not specified
        format (str): if data_source=="rest": csv, json, or url, default csv. if data_source=="aws": df or xarray
        data_source (str): location to query for data, either 'rest' or 'aws'. default is aws.

    Returns:
        pd.DataFrame or dict or str
    """
    pass


@_forecast_endpoint_decorator
def forecast_records(*, river_id: int, start_date: str, end_date: str, format: str,
                     **kwargs) -> pd.DataFrame or dict or str:
    """
    Retrieves a csv showing the ensemble average forecasted flow for the year from January 1 to the current date

    Keyword Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        start_date (str): a YYYYMMDD string giving the earliest date this year to include, defaults to 14 days ago.
        end_date (str): a YYYYMMDD string giving the latest date this year to include, defaults to latest available
        format (str): csv, json, or url, default csv.

    Returns:
        pd.DataFrame or dict or str
    """
    pass


# Retrospective simulation and derived products
def retrospective(river_id: int or list, format: str = 'df') -> pd.DataFrame or xr.Dataset:
    """
    Retrieves the retrospective simulation of streamflow for a given river_id from the
    AWS Open Data Program GEOGLOWS V2 S3 bucket

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        format (str): the format to return the data, either 'df' or 'xarray'. default is 'df'

    Returns:
        pd.DataFrame
    """
    s3 = s3fs.S3FileSystem(anon=True, client_kwargs=dict(region_name=ODP_S3_BUCKET_REGION))
    s3store = s3fs.S3Map(root=f'{ODP_RETROSPECTIVE_S3_BUCKET_URI}/retrospective.zarr', s3=s3, check=False)
    ds = xr.open_zarr(s3store).sel(rivid=river_id)
    if format == 'xarray':
        return ds
    return ds.to_dataframe().reset_index().set_index('time').pivot(columns='rivid', values='Qout')


def historical(*args, **kwargs):
    """Alias for retrospective"""
    return retrospective(*args, **kwargs)


def daily_averages(river_id: int or list) -> pd.DataFrame:
    """
    Retrieves daily average streamflow for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(river_id)
    return calc_daily_averages(df)


def monthly_averages(river_id: int or list) -> pd.DataFrame:
    """
    Retrieves monthly average streamflow for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(river_id)
    return calc_monthly_averages(df)


def annual_averages(river_id: int or list) -> pd.DataFrame:
    """
    Retrieves annual average streamflow for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(river_id)
    return calc_annual_averages(df)


def return_periods(river_id: int or list, format: str = 'df') -> pd.DataFrame or xr.Dataset:
    """
    Retrieves the return period thresholds based on a specified historic simulation forcing on a certain river_id.

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        format (str): the format to return the data, either 'df' or 'xarray'. default is 'df'

    Returns:
        pd.DataFrame
    """
    s3 = s3fs.S3FileSystem(anon=True, client_kwargs=dict(region_name=ODP_S3_BUCKET_REGION))
    s3store = s3fs.S3Map(root=f'{ODP_RETROSPECTIVE_S3_BUCKET_URI}/return-periods.zarr', s3=s3, check=False)
    ds = xr.open_zarr(s3store).sel(rivid=river_id)
    if format == 'xarray':
        return ds
    return (ds['return_period_flow'].to_dataframe().reset_index()
            .pivot(index='rivid', columns='return_period', values='return_period_flow'))


# model config and supplementary data
def metadata_tables(columns: list = None) -> pd.DataFrame:
    """
    Retrieves the master table of rivers metadata and properties as a pandas DataFrame
    Args:
        columns (list): optional subset of columns names to read from the parquet

    Returns:
        pd.DataFrame
    """
    if os.path.exists(METADATA_TABLE_PATH):
        return pd.read_parquet(METADATA_TABLE_PATH, columns=columns)
    warn = f"""
    Local copy of geoglows v2 metadata table not found. You should download a copy for optimal performance and 
    to make the data available when you are offline. A copy of the table will be cached at {METADATA_TABLE_PATH}.
    Alternatively, set the environment variable PYGEOGLOWS_METADATA_TABLE_PATH to the path of the table.
    """
    warnings.warn(warn)
    df = pd.read_parquet('https://geoglows-v2.s3-website-us-west-2.amazonaws.com/tables/package-metadata-table.parquet')
    os.makedirs(os.path.dirname(METADATA_TABLE_PATH), exist_ok=True)
    df.to_parquet(METADATA_TABLE_PATH)
    return df[columns] if columns else df
