import os
import warnings
import numpy as np
import pandas as pd
import xarray as xr

from ._constants import get_metadata_table_path, get_sfdc_table_path, get_saber_assign_table_path, get_fdc_table_path
from ._download_decorators import _forecast, _retrospective, DEFAULT_REST_ENDPOINT, DEFAULT_REST_ENDPOINT_VERSION

from .analyze import (
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
    'lookup_assign_saber_table',
    'retrieve_sfdc',
    'retrieve_sfdc_for_river_id',

    'metadata_tables',
    'saber_assign_table',
    'sfdc_table',
    'fdc_table',

    'DEFAULT_REST_ENDPOINT',
    'DEFAULT_REST_ENDPOINT_VERSION',
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
def retrospective(river_id: int or list, *, format: str = 'df') -> pd.DataFrame or xr.Dataset:
    """
    Retrieves the retrospective simulation of streamflow for a given river_id from the
    AWS Open Data Program GEOGLOWS V2 S3 bucket

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        format (str): the format to return the data, either 'df' or 'xarray'. default is 'df'

    Returns:
        pd.DataFrame
    """
    pass


def daily_averages(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves daily average streamflow for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(river_id, **kwargs)
    return calc_daily_averages(df)


def monthly_averages(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves monthly average streamflow for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(river_id, **kwargs)
    return calc_monthly_averages(df)


def annual_averages(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves annual average streamflow for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    df = retrospective(river_id, **kwargs)
    return calc_annual_averages(df)

def lookup_assign_saber_table(river_id: int or list, saber_assign_table_path: str = None) -> list:
    """
    Retrieves 'asgn_mid' values from the SABER assign table for the given river_id(s).

    Args:
        river_id (int or list): ID(s) of a stream(s), should be a 9-digit integer or a list of such integers.
        saber_assign_table_path (str): Path to the local copy of the SABER assign table.

    Returns:
        list: List of 'asgn_mid' values for given river_id.
    """
    if hasattr(river_id, 'item'):
        river_id = river_id.item()
    if isinstance(river_id, (int, np.integer)):
        river_id = [river_id]
    elif isinstance(river_id, list):
        if not all(isinstance(x, int) for x in river_id):
            raise ValueError("All river_id values must be integers")
    else:
        raise ValueError("river_id must be an integer or a list of integers")
    if hasattr(river_id, 'item'):
        river_id = river_id.item()

    # Read the SABER assign table into a DataFrame
    df = pd.read_parquet(saber_assign_table_path=saber_assign_table_path)
    asgn_mid = df.loc[df['model_id'].isin(river_id), 'asgn_mid'].tolist()

    return asgn_mid


def retrieve_sfdc(asgn_mid: int or list, sfdc_table_path: str = None) -> pd.DataFrame:
    """
    Retrieves data from the SFDC table based on 'asgn_mid' values for given river_id.

    Args:
        asgn_mid (int or list): Single or list of 'asgn_mid' values to filter the SFDC table.
        sfdc_table_path (str): Path to the copy of the SFDC table.

    Returns:
        pd.DataFrame: Filtered DataFrame based on 'asgn_mid' values from the SFDC table.
    """
    # Read the SFDC table into a DataFrame
    ds = xr.open_zarr(sfdc_table_path= sfdc_table_path)
    # Filter the dataset based on 'asgn_mid' matching 'rivid'
    filtered_ds = ds.sel(rivid=asgn_mid)
    return filtered_ds.to_dataframe().reset_index()


def retrieve_sfdc_for_river_id(river_id: int or list, sfdc_table_path: str = None,
                                saber_assign_table_path: str = None) -> pd.DataFrame:
    """
    Retrieves data from the SFDC table using 'asgn_mid' values obtained from the SABER assign table for the given 'river_id'.

    Args:
        river_id (int or list): ID(s) of a stream(s).
        sfdc_table_path (str): Path to the local copy of the SFDC table.
        saber_assign_table_path (str): Path to the local copy of the SABER assign table.

    Returns:
        pd.DataFrame: Filtered DataFrame from the SFDC table based on 'asgn_mid' values.
    """
    # Step 1: Get 'asgn_mid' values for the given river_id(s)
    asgn_mids = lookup_assign_saber_table(river_id)
    # Step 2: Retrieve SFDC data based on 'asgn_mid' values
    filtered_sfdc = retrieve_sfdc(asgn_mids)
    return filtered_sfdc

def retrieve_fdc(river_id: int or list, fdc_table_path: str = None) -> pd.DataFrame:
    """
    Retrieves data from the FDC table based on river_id.

    Args:
        river_id (int or list): Single or list of unique river identifier to filter the FDC table.
        fdc_table_path (str): Path to the local copy of the FDC table.

    Returns:
        pd.DataFrame: Filtered DataFrame based on 'asgn_mid' values from the FDC table.
    """
    if hasattr(river_id, 'item'):
        river_id = river_id.item()
    if isinstance(river_id, (int, np.integer)):
        river_id = [river_id]
        # Check if list contains only integers
    elif isinstance(river_id, list):
        if not all(isinstance(x, int) for x in river_id):
            raise ValueError("All river_id values must be integers")
    else:
        raise ValueError("river_id must be an integer or a list of integers")

        # Open and filter the dataset
    df = xr.open_zarr(fdc_table_path)
    fdc = df.sel(rivid=river_id)
    return fdc.to_dataframe().reset_index()

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


def saber_assign_table(columns: list = None, saber_table_path: str = None) -> pd.DataFrame:
    """
    Retrieves the SABER assign table as a pandas DataFrame

    Args:
        columns (list): optional subset of column names to read from the parquet
        saber_table_path (str): optional path to a local copy of the SABER assign table

    Returns:
        pd.DataFrame
    """
    if saber_table_path:
        return pd.read_parquet(saber_table_path, columns=columns)
    saber_table_path = get_saber_assign_table_path()
    if os.path.exists(saber_table_path):
        return pd.read_parquet(saber_table_path, columns=columns)

    warn = f"""
    Local copy of SABER assign table not found.
    A copy of the table has been cached at {saber_table_path} which you can move as desired.
    You should set the environment variable PYGEOGLOWS_SABER_ASSIGN_TABLE_PATH or provide the saber_table_path argument.
    """
    warnings.warn(warn)

    # Assuming the S3 URL for the SABER assign table. You may need to adjust this URL.
    df = pd.read_parquet('http://geoglows-v2.s3-website-us-west-2.amazonaws.com/tables/saber-assign-table.parquet')

    os.makedirs(os.path.dirname(saber_table_path), exist_ok=True)
    df.to_parquet(saber_table_path)

    return df[columns] if columns else df


def sfdc_table(columns: list = None, sfdc_table_path: str = None) -> pd.DataFrame:
    """
    Retrieves the SFDC table as a pandas DataFrame

    Args:
        columns (list): optional subset of column names to read from the parquet
        sfdc_table_path (str): optional path to a local copy of the SFDC table

    Returns:
        pd.DataFrame
    """
    if sfdc_table_path:
        return pd.read_parquet(sfdc_table_path, columns=columns)

    sfdc_table_path = get_sfdc_table_path()
    if os.path.exists(sfdc_table_path):
        return pd.read_parquet(sfdc_table_path, columns=columns)

    warn = f"""
    Local copy of SFDC table not found.
    A copy of the table has been cached at {sfdc_table_path} which you can move as desired.
    You should set the environment variable PYGEOGLOWS_SFDC_TABLE_PATH or provide the sfdc_table_path argument.
    """
    warnings.warn(warn)

    df = pd.read_parquet('http://geoglows-v2.s3-website-us-west-2.amazonaws.com/tables/sfdc-removing-zero.parquet')
    os.makedirs(os.path.dirname(sfdc_table_path), exist_ok=True)
    df.to_parquet(sfdc_table_path)

    return df[columns] if columns else df

def fdc_table(columns: list = None, fdc_table_path: str = None) -> pd.DataFrame:
    """
    Retrieves the FDC table as a pandas DataFrame

    Args:
        columns (list): optional subset of column names to read from the parquet
        fdc_table_path (str): optional path to a local copy of the FDC table

    Returns:
        pd.DataFrame
    """
    if fdc_table_path:
        return pd.read_parquet(fdc_table_path, columns=columns)

    fdc_table_path = get_fdc_table_path()
    if os.path.exists(fdc_table_path):
        return pd.read_parquet(fdc_table_path, columns=columns)

    warn = f"""
    Local copy of FDC table not found.
    A copy of the table has been cached at {fdc_table_path} which you can move as desired.
    You should set the environment variable PYGEOGLOWS_FDC_TABLE_PATH or provide the fdc_table_path argument.
    """
    warnings.warn(warn)

    df = pd.read_parquet('http://geoglows-v2.s3-website-us-west-2.amazonaws.com/tables/simulated_monthly.parquet')
    os.makedirs(os.path.dirname(fdc_table_path), exist_ok=True)
    df.to_parquet(fdc_table_path)

    return df[columns] if columns else df