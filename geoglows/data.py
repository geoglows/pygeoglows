import os

import pandas as pd
import requests
import s3fs
import xarray as xr

__all__ = [
    'forecast',
    'forecast_stats',
    'forecast_ensembles',
    'forecast_records',
    'forecast_dates',
    'retrospective',
    'daily_averages',
    'monthly_averages',
    'annual_averages',
    'return_periods',
]

DEFAULT_REST_ENDPOINT = 'https://geoglows.ecmwf.int/api/'
DEFAULT_REST_ENPOINT_VERSION = 'v2'  # 'v1, v2, latest'
ODP_S3_BUCKET_URI = 's3://geoglows-v2'
ODP_S3_BUCKET_REGION = 'us-west-2'


def _forecast_endpoint_decorator(function):
    def wrapper(**kwargs):
        # update the default values set by the function unless the user has already specified them
        for key, value in function.__kwdefaults__.items():
            if key not in kwargs:
                kwargs[key] = value

        # parse out the information necessary to build a request url
        endpoint = kwargs.get('endpoint', DEFAULT_REST_ENDPOINT)
        endpoint = endpoint[:-1] if endpoint[-1] == '/' else endpoint

        version = kwargs.get('version', DEFAULT_REST_ENPOINT_VERSION)

        product_name = function.__name__.replace("_", "").lower()

        reach_id = kwargs.get('reach_id', '')
        reach_id = f'/{reach_id}' if reach_id else reach_id

        return_format = kwargs.get('return_format', 'csv')
        assert return_format in ('csv', 'json', 'url'), f'Unsupported return format requested: {return_format}'

        # request parameter validation before submitting
        for key in ('endpoint', 'version'):
            if key in kwargs:
                del kwargs[key]
        for key, value in kwargs.items():
            if value is None:
                del kwargs[key]
        for date in ('date', 'start_date', 'end_date'):
            if date in kwargs:
                assert pd.to_datetime(kwargs[date], format='%Y%m%d'), f'{date} must be a string in YYYYMMDD format'
        if 'return_format' in kwargs and kwargs['return_format'] != 'json':
            del kwargs['return_format']  # csv is the default, url is only a python function response
        kwargs['source'] = kwargs.get('source', 'pygeoglows')  # allow using default for specific apps which override
        params = '&'.join([f'{key}={value}' for key, value in kwargs.items()])

        # piece together the request url
        request_url = f'{endpoint}/{version}/{product_name}{reach_id}?{params}'

        if return_format == 'url':
            return request_url

        response = requests.get(request_url)

        if response.status_code != 200:
            raise RuntimeError('Recieved an error from the Streamflow REST API: ' + response.text)

        if return_format == 'json':
            return response.json()
        elif return_format == 'csv':
            return pd.read_csv(response.text)
        else:
            raise ValueError(f'Unsupported return format requested: {return_format}')

    return wrapper


# Forecast data and derived products
@_forecast_endpoint_decorator
def forecast_dates(**kwargs) -> dict or str:
    """
    Gets a list of available forecast product dates

    Keyword Args:
        return_format: csv, json, or url, default csv
        endpoint: the endpoint of an api instance, only applicable for package or rest endpoint developers

    Returns:
        pd.DataFrame or dict

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
        return_format: csv, json, or url, default csv
        endpoint: the endpoint of an api instance, only applicable for package or rest endpoint developers

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
        return_format: csv, json, or url, default csv
        endpoint: the endpoint of an api instance, only applicable for package or rest endpoint developers

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
        return_format: csv, json, or url, default csv
        endpoint: the endpoint of an api instance, only applicable for package or rest endpoint developers

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
        return_format: csv, json, or url, default csv
        endpoint: the endpoint of an api instance, only applicable for package or rest endpoint developers

    Returns:
        pd.DataFrame or dict or str

    """
    pass


# Retrospective simulation and derived products
def retrospective(reach_id: int) -> pd.DataFrame:
    """
    Retrieves the retrospective simulation of streamflow for a given reach_id from the
    AWS Open Data Program GEOGloWS V2 S3 bucket

    Args:
        reach_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    s3 = s3fs.S3FileSystem(anon=True, client_kwargs=dict(region_name=ODP_S3_BUCKET_REGION))
    s3store = s3fs.S3Map(root=f'{ODP_S3_BUCKET_URI}/retro.zarr', s3=s3, check=False)
    return xr.open_zarr(s3store).sel(rivid=reach_id).to_dataframe().reset_index().set_index('time').pivot(columns='rivid', values='Qout')


def historical(*args, **kwargs):
    """Alias for retrospective"""
    return retrospective(*args, **kwargs)


def daily_averages(reach_id: int) -> pd.DataFrame:
    """
    Retrieves daily average streamflow for a given reach_id

    Args:
        reach_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(reach_id)
    return df.groupby(df.index.strftime('%m%d')).rolling(5).mean()


def monthly_averages(reach_id: int) -> pd.DataFrame:
    """
    Retrieves monthly average streamflow for a given reach_id

    Args:
        reach_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(reach_id)
    return df.groupby(df.index.strftime('%m')).mean()


def annual_averages(reach_id: int) -> pd.DataFrame:
    """
    Retrieves annual average streamflow for a given reach_id

    Args:
        reach_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(reach_id)
    return df.groupby(df.index.strftime('%Y')).mean()


def return_periods(reach_id: int) -> pd.DataFrame:
    """
    Retrieves the return period thresholds based on a specified historic simulation forcing on a certain reach_id.

    Args:
        reach_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    s3 = s3fs.S3FileSystem(anon=True, client_kwargs=dict(region_name=ODP_S3_BUCKET_REGION))
    s3store = s3fs.S3Map(root=f'{ODP_S3_BUCKET_URI}/return-periods.zarr', s3=s3, check=False)
    return xr.open_zarr(s3store).sel(rivid=reach_id).to_dataframe()


# model config and supplementary data
def master_table(columns: list = None) -> pd.DataFrame or None:
    """
    Retrieves the master table of stream reaches with all metadata and properties as a pandas DataFrame
    Args:
        columns: optional subset of columns names to read from the parquet

    Returns:
        pd.DataFrame
    """
    s3_table_path = 's3://geoglows-v2/geoglows-v2-master-table.parquet'
    return pd.read_parquet(s3_table_path, columns=columns)