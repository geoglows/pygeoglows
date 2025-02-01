import os
import warnings

import pandas as pd
import xarray as xr

from ._constants import get_metadata_table_path, get_transformer_table_uri
from ._download_decorators import _forecast, _retrospective, _transformer


__all__ = [
    # forecast products
    'dates',
    'forecast',
    'forecast_stats',
    'forecast_ensembles',
    'forecast_records',

    # retrospective products
    'retrospective',
    'retrospective_hourly',
    'retrospective_daily',
    'retrospective_monthly',
    'retrospective_yearly',
    'retrospective_monthly_timeseries',
    'retrospective_monthly_timesteps',
    'retrospective_yearly_timeseries',
    'retrospective_yearly_timesteps',
    'return_periods',
    'annual_maximums',

    # transformers
    'sfdc',
    'wse',
    'transform_curve_ids',
    'sfdc_for_river_id',
    'wse_for_river_id',

    # metadata
    'metadata_tables',
]


# Forecast data and derived products
@_forecast
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


@_forecast
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


@_forecast
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


@_forecast
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


@_forecast
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
@_retrospective
def retrospective(river_id: int or list,
                  *, resolution: str = 'daily', format: str = 'df') -> pd.DataFrame or xr.Dataset:
    """
    Retrieves the retrospective simulation of streamflow for a given river_id from the
    AWS Open Data Program GEOGLOWS V2 S3 bucket

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        resolution (str): the time step of the data: 'hourly' (default), 'daily', 'monthly', or 'yearly.
        format (str): the format to return the data, either 'df' or 'xarray'. default is 'df'

    Returns:
        pd.DataFrame
    """
    pass


def retrospective_hourly(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves hourly retrospective streamflow simulation for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    return retrospective(river_id, resolution='hourly', **kwargs)


def retrospective_daily(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves daily retrospective streamflow simulation for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    return retrospective(river_id, resolution='daily', **kwargs)


def retrospective_monthly(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves monthly retrospective streamflow simulation for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    return retrospective_monthly_timeseries(river_id, **kwargs)


def retrospective_yearly(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves yearly retrospective streamflow simulation for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    return retrospective(river_id, resolution='yearly-timeseries', **kwargs)


def retrospective_monthly_timeseries(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves monthly retrospective streamflow simulation for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    return retrospective(river_id, resolution='monthly-timeseries', **kwargs)


def retrospective_monthly_timesteps(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves monthly retrospective streamflow simulation for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    return retrospective(river_id, resolution='monthly-timesteps', **kwargs)


def retrospective_yearly_timeseries(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves yearly retrospective streamflow simulation for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    return retrospective(river_id, resolution='yearly-timeseries', **kwargs)


def retrospective_yearly_timesteps(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves yearly retrospective streamflow simulation for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    return retrospective(river_id, resolution='yearly-timesteps', **kwargs)


@_retrospective
def return_periods(river_id: int or list, *, format: str = 'df', method: str = 'gumbel1') -> pd.DataFrame or xr.Dataset:
    """
    Retrieves the return period thresholds based on a specified historic simulation forcing on a certain river_id.

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        format (str): the format to return the data, either 'df' or 'xarray'. default is 'df'
        method (str): the method to use to estimate the return period thresholds. default is 'gumbel1'

    Changelog:
        v1.4.0: adds method parameter for future expansion of multiple return period methods

    Returns:
        pd.DataFrame
    """
    pass


@_retrospective
def annual_maximums(river_id: int or list) -> pd.DataFrame:
    """
    Retrieves the annual maximum streamflow for a given river_id based on hourly retrospective simulation data.

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    pass


@_transformer
def sfdc(curve_id: int or list) -> pd.DataFrame:
    """
    Retrieves data from the SFDC table based on 'asgn_mid' values for given river_id.

    Args:
        curve_id (int or list): Single or list of sfdc curve IDs

    Returns:
        pd.DataFrame
    """
    pass


@_transformer
def wse(curve_id: int or list) -> pd.DataFrame:
    """
    Retrieves data from the WSE table based on 'asgn_mid' values for given river_id.

    Args:
        curve_id (int or list): Single or list of wse curve IDs

    Returns:
        pd.DataFrame
    """
    # todo update decorator
    pass


@_transformer
def transform_table() -> pd.DataFrame:
    """
    Retrieves the SABER assign table as a pandas DataFrame.

    Returns:
        pd.DataFrame
    """
    # todo update decorator
    pass


def transform_curve_ids(river_id: int) -> dict:
    """
    Retrieves 'asgn_mid' values from the SABER assign table for the given river_id(s).

    Args:
        river_id (int or list): ID(s) of a stream(s), should be a 9-digit integer or a list of such integers.

    Returns:
        list: List of 'asgn_mid' values for given river_id.
    """
    assert isinstance(river_id, int), 'river_id must be an integer'
    df = pd.read_parquet(get_transformer_table_uri())
    # make a dictionary of column: value pairs
    curve_ids = df.loc[df['river_id'] == river_id].to_dict(orient='records')[0]
    return curve_ids


def sfdc_for_river_id(river_id: int) -> pd.DataFrame:
    """
    Retrieves data from the SFDC table using 'asgn_mid' values obtained from the SABER assign table for the given 'river_id'.

    Args:
        river_id (int or list): ID(s) of a stream(s).

    Returns:
        pd.DataFrame: Filtered DataFrame from the SFDC table based on 'asgn_mid' values.
    """
    assert isinstance(river_id, int), 'river_id must be an integer'
    curve_ids = transform_curve_ids(river_id)['sfdc_curve_id']
    return sfdc(curve_ids)


def wse_for_river_id(river_id: int) -> pd.DataFrame:
    """
    Retrieves data from the WSE table using 'asgn_mid' values obtained from the SABER assign table for the given 'river_id'.

    Args:
        river_id (int or list): ID(s) of a stream(s).

    Returns:
        pd.DataFrame: Filtered DataFrame from the WSE table based on 'asgn_mid' values.
    """
    assert isinstance(river_id, int), 'river_id must be an integer'
    curve_ids = transform_curve_ids(river_id)['wse_curve_id']
    return wse(curve_ids)


# model config and supplementary data
def metadata_tables(columns: list = None, metadata_table_path: str = None) -> pd.DataFrame:
    """
    Retrieves the master table of rivers metadata and properties as a pandas DataFrame
    Args:
        columns (list): optional subset of columns names to read from the parquet
        metadata_table_path (str): optional path to a local copy of the metadata table

    Returns:
        pd.DataFrame
    """
    if metadata_table_path:
        return pd.read_parquet(metadata_table_path, columns=columns)
    metadata_table_path = get_metadata_table_path()
    if os.path.exists(metadata_table_path):
        return pd.read_parquet(metadata_table_path, columns=columns)
    warn = f"""
    Local copy of geoglows v2 metadata table not found.
    A copy of the table has been cached at {metadata_table_path} which you can move as desired.
    You should set the environment variable PYGEOGLOWS_METADATA_TABLE_PATH or provide the metadata_table_path argument.
    """
    warnings.warn(warn)
    df = pd.read_parquet('http://geoglows-v2.s3-website-us-west-2.amazonaws.com/tables/package-metadata-table.parquet')
    os.makedirs(os.path.dirname(metadata_table_path), exist_ok=True)
    df.to_parquet(metadata_table_path)
    return df[columns] if columns else df
