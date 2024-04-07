import os
import warnings
from io import StringIO

import pandas as pd
import requests
import s3fs
import xarray as xr

from ._constants import METADATA_TABLE_LOCAL_PATH
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

        reach_id = args[0] if len(args) > 0 else None
        reach_id = kwargs.get('reach_id', '') if not reach_id else reach_id

        s3 = s3fs.S3FileSystem(anon=True, client_kwargs=dict(region_name=ODP_S3_BUCKET_REGION))
        if kwargs.get('date', '') and not product_name == 'dates':
            date = kwargs['date']
            if len(date) == 8:
                date = f'{date}00.zarr'
            elif len(date) == 10:
                date = f'{date}.zarr'
            else:
                raise ValueError('Date must be YYYYMMDD or YYYYMMDDHH format. Use dates() to view available data.')
        else:
            dates = sorted([x.split('/')[-1] for x in s3.ls(ODP_FORECAST_S3_BUCKET_URI)])
            if product_name == 'dates':
                return dates
            date = dates[-1]
        s3store = s3fs.S3Map(root=f'{ODP_FORECAST_S3_BUCKET_URI}/{date}', s3=s3, check=False)

        df = xr.open_zarr(s3store).sel(rivid=reach_id).to_dataframe().round(2).reset_index()

        # rename columns to match the REST API
        if type(reach_id) is list:
            df = df.pivot(columns='ensemble', index=['time', 'rivid'], values='Qout')
        else:
            df = df.pivot(index='time', columns='ensemble', values='Qout')
        df = df[sorted(df.columns)]
        df.columns = [f'ensemble_{str(x).zfill(2)}' for x in df.columns]

        if product_name == 'forecastensembles':
            return df
        elif product_name == 'forecaststats':
            return calc_forecast_stats(df)
        elif product_name == 'forecast':
            return calc_simple_forecast(df)
        return

    def from_rest(*args, **kwargs):
        # update the default values set by the function unless the user has already specified them
        for key, value in function.__kwdefaults__.items() if function.__kwdefaults__ else []:
            if key not in kwargs:
                kwargs[key] = value

        return_url = kwargs.get('format', 'csv') == 'url'

        # parse out the information necessary to build a request url
        endpoint = kwargs.get('endpoint', DEFAULT_REST_ENDPOINT)
        endpoint = endpoint[:-1] if endpoint[-1] == '/' else endpoint
        endpoint = endpoint + '/api' if not endpoint.endswith('/api') else endpoint
        endpoint = f'https://{endpoint}' if not endpoint.startswith(('https://', 'http://')) else endpoint

        version = kwargs.get('version', DEFAULT_REST_ENDPOINT_VERSION)

        product_name = function.__name__.replace("_", "").lower()

        reach_id = args[0] if len(args) > 0 else None
        reach_id = kwargs.get('reach_id', '') if not reach_id else reach_id

        return_format = kwargs.get('return_format', 'csv')
        assert return_format in ('csv', 'json', 'url'), f'Unsupported return format requested: {return_format}'

        # request parameter validation before submitting
        for key in ('endpoint', 'version', 'reach_id'):
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
        request_url = f'{request_url}/{reach_id}' if reach_id else request_url  # add the reach_id if it exists
        request_url = f'{request_url}?{params}'  # add the query parameters

        if return_url:
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
        source = kwargs.get('data_source', 'rest')
        assert source in ('rest', 'aws'), ValueError(f'Unrecognized data source requested: {source}')
        if source == 'rest':
            return from_rest(*args, **kwargs)
        else:
            return from_aws(*args, **kwargs)

    return main


# Forecast data and derived products
@_forecast_endpoint_decorator
def dates(**kwargs) -> dict or str:
    """
    Gets a list of available forecast product dates

    Keyword Args:
        format: csv, json, or url, default csv
        data_source: location to query for data, either 'rest' or 'aws'

    Returns:
        dict or str

        the csv is a single column with a header of 'available_dates' and 1 row per date, sorted oldest to newest
        The dictionary structure is {'available_dates': ['list', 'of', 'dates', 'YYYYMMDD', 'format']}
    """
    pass


@_forecast_endpoint_decorator
def forecast(*, reach_id: int, **kwargs) -> pd.DataFrame or dict or str:
    """
    Gets the average forecasted flow for a certain reach_id on a certain date

    Keyword Args:
        reach_id: the ID of a stream, should be a 9 digit integer
        date: a string specifying the date to request in YYYYMMDD format, returns the latest available if not specified
        format: csv, json, or url, default csv
        data_source: location to query for data, either 'rest' or 'aws'

    Returns:
        pd.DataFrame or dict or str
    """
    pass


@_forecast_endpoint_decorator
def forecast_stats(*, reach_id: int, **kwargs) -> pd.DataFrame or dict or str:
    """
    Retrieves the min, 25%, mean, median, 75%, and max river discharge of the 51 ensembles members for a reach_id
    The 52nd higher resolution member is excluded

    Keyword Args:
        reach_id: the ID of a stream, should be a 9 digit integer
        date: a string specifying the date to request in YYYYMMDD format, returns the latest available if not specified
        format: csv, json, or url, default csv
        data_source: location to query for data, either 'rest' or 'aws'

    Returns:
        pd.DataFrame or dict or str
    """
    pass


@_forecast_endpoint_decorator
def forecast_ensembles(*, reach_id: int, **kwargs) -> pd.DataFrame or dict or str:
    """
    Retrieves each of 52 time series of forecasted discharge for a reach_id on a certain date

    Keyword Args:
        reach_id: the ID of a stream, should be a 9 digit integer
        date: a string specifying the date to request in YYYYMMDD format, returns the latest available if not specified
        format: csv, json, or url, default csv
        data_source: location to query for data, either 'rest' or 'aws'

    Returns:
        pd.DataFrame or dict or str
    """
    pass


@_forecast_endpoint_decorator
def forecast_records(*, reach_id: int, **kwargs) -> pd.DataFrame or dict or str:
    """
    Retrieves a csv showing the ensemble average forecasted flow for the year from January 1 to the current date

    Keyword Args:
        reach_id: the ID of a stream, should be a 9 digit integer
        start_date: a YYYYMMDD string giving the earliest date this year to include, defaults to YYYY0101
        end_date: a YYYYMMDD string giving the latest date this year to include, defaults to latest available
        format: csv, json, or url, default csv

    Returns:
        pd.DataFrame or dict or str
    """
    pass


# Retrospective simulation and derived products
def retrospective(reach_id: int or list) -> pd.DataFrame:
    """
    Retrieves the retrospective simulation of streamflow for a given reach_id from the
    AWS Open Data Program GEOGloWS V2 S3 bucket

    Args:
        reach_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    s3 = s3fs.S3FileSystem(anon=True, client_kwargs=dict(region_name=ODP_S3_BUCKET_REGION))
    s3store = s3fs.S3Map(root=f'{ODP_RETROSPECTIVE_S3_BUCKET_URI}/retrospective.zarr', s3=s3, check=False)
    return (xr.open_zarr(s3store).sel(rivid=reach_id).to_dataframe().reset_index().set_index('time')
            .pivot(columns='rivid', values='Qout'))


def historical(*args, **kwargs):
    """Alias for retrospective"""
    return retrospective(*args, **kwargs)


def daily_averages(reach_id: int or list) -> pd.DataFrame:
    """
    Retrieves daily average streamflow for a given reach_id

    Args:
        reach_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(reach_id)
    return calc_daily_averages(df)


def monthly_averages(reach_id: int or list) -> pd.DataFrame:
    """
    Retrieves monthly average streamflow for a given reach_id

    Args:
        reach_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(reach_id)
    return calc_monthly_averages(df)


def annual_averages(reach_id: int or list) -> pd.DataFrame:
    """
    Retrieves annual average streamflow for a given reach_id

    Args:
        reach_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(reach_id)
    return calc_annual_averages(df)


def return_periods(reach_id: int or list) -> pd.DataFrame:
    """
    Retrieves the return period thresholds based on a specified historic simulation forcing on a certain reach_id.

    Args:
        reach_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    s3 = s3fs.S3FileSystem(anon=True, client_kwargs=dict(region_name=ODP_S3_BUCKET_REGION))
    s3store = s3fs.S3Map(root=f'{ODP_RETROSPECTIVE_S3_BUCKET_URI}/return-periods.zarr', s3=s3, check=False)
    return (xr.open_zarr(s3store).sel(rivid=reach_id)['return_period_flow'].to_dataframe().reset_index()
            .pivot(index='rivid', columns='return_period', values='return_period_flow'))


# model config and supplementary data
def metadata_tables(columns: list = None) -> pd.DataFrame:
    """
    Retrieves the master table of stream reaches with all metadata and properties as a pandas DataFrame
    Args:
        columns: optional subset of columns names to read from the parquet

    Returns:
        pd.DataFrame
    """
    if os.path.exists(METADATA_TABLE_LOCAL_PATH):
        return pd.read_parquet(METADATA_TABLE_LOCAL_PATH, columns=columns)
    warn = f"""
    Local copy of geoglows v2 metadata table not found. You should download a copy for optimal performance and 
    to make the data available when you are offline. A copy of the table will be cached at {METADATA_TABLE_LOCAL_PATH}.
    """
    warnings.warn(warn)
    df = pd.read_parquet('s3://geoglows-v2/tables/package-metadata-table.parquet')
    os.makedirs(os.path.dirname(METADATA_TABLE_LOCAL_PATH), exist_ok=True)
    df.to_parquet(METADATA_TABLE_LOCAL_PATH)
    return df[columns] if columns else df
