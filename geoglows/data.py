import os
import warnings

import numpy as np
import pandas as pd
import xarray as xr

from ._constants import get_uri
from ._download_decorators import _forecast, _retrospective, DEFAULT_REST_ENDPOINT, DEFAULT_REST_ENDPOINT_VERSION

__all__ = [
    # forecast products
    'dates',
    'forecast',
    'forecast_stats',
    'forecast_ensembles',
    'forecast_records',

    # retrospective products
    'retrospective',
    'daily_averages',
    'monthly_averages',
    'annual_averages',
    'fdc',
    'return_periods',

    # transformers
    'sfdc',
    'hydroweb_wse_transformer',

    # metadata
    'metadata_tables',

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


@_retrospective
def daily_averages(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves daily average streamflow for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        format (str): the format to return the data, either 'df' or 'xarray'. default is 'df'

    Returns:
        pd.DataFrame
    """
    pass


@_retrospective
def monthly_averages(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves monthly average streamflow for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        format (str): the format to return the data, either 'df' or 'xarray'. default is 'df'

    Returns:
        pd.DataFrame
    """
    pass


@_retrospective
def annual_averages(river_id: int or list, **kwargs) -> pd.DataFrame:
    """
    Retrieves annual average streamflow for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        format (str): the format to return the data, either 'df' or 'xarray'. default is 'df'

    Returns:
        pd.DataFrame
    """
    pass


@_retrospective
def fdc(river_id: int or list, *,
        format: str = 'df', resolution: str = 'daily', kind: str = 'monthly') -> pd.DataFrame or xr.Dataset:
    """
    Retrieves the flow duration curve for a given river_id

    Args:
        river_id (int): the ID of a stream, should be a 9 digit integer
        format (str): the format to return the data, either 'df' or 'xarray'. default is 'df'
        resolution (str): time step of the retrospective data used to calculate the fdc, either 'daily' or 'hourly'.
        kind (str): retrieve either the 'total' FDC (all values considered, returns 1 curve)
            or 'monthly' (12 curves, each using values in that month)

    Returns:
        pd.DataFrame or xr.Dataset
    """
    pass


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


# @_transformer
def sfdc(*, curve_id: int or list = None, river_id: int or list = None) -> pd.DataFrame:
    """
    Retrieves data from the SFDC table based on 'asgn_mid' values for given river_id.

    Args:
        curve_id (int or list): the ID of an sfdcd transformer curve, should be a 12 digit integer
        river_id (int): the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    # check that curve_id is a 12 digit integer or a list of such integers
    if isinstance(curve_id, (int, np.integer)):
        assert len(str(curve_id)) == 12, "curve_id must be a 12 digit integer"
    if isinstance(curve_id, list):
        assert all(len(str(x)) == 12 for x in curve_id), "curve_id must be a 12 digit integer"
        assert all(isinstance(x, int) for x in curve_id), "curve_id must be a 12 digit integer"
    if curve_id is None and river_id is None:
        raise ValueError("curve_id or river_id must be provided")
    if curve_id is not None and river_id is not None:
        raise ValueError("curve_id and river_id cannot both be provided")

    if river_id is not None:
        assert isinstance(river_id, int), 'river_id must be an integer'
        curve_id = pd.read_parquet(get_uri('transformer_table')).loc[river_id, 'sfdc_curve_id']

    uri = get_uri('sfdc')
    storage_options = {'anon': True} if uri.startswith('s3://rfs-v2') else None
    return (
        xr
        .open_zarr(uri, storage_options=storage_options)
        .sel(curve_id=curve_id)
        .to_dataframe()
        .reset_index()
        .pivot(index=['month', 'p_exceed'], values='sfdc', columns='curve_id')
    )


# @_transformer
def hydroweb_wse_transformer(river_id: int) -> pd.DataFrame:
    """
    Retrieves a water surface elevation transform curves only for select rivers with hydroweb observations
    Args:
        river_id: the ID of a stream, should be a 9 digit integer

    Returns:
        pd.DataFrame
    """
    uri = get_uri('hydroweb')
    storage_options = {'anon': True} if uri.startswith('s3://rfs-v2') else None
    with xr.open_zarr(uri, storage_options=storage_options) as ds:
        try:
            return ds.sel(river_id=river_id).to_dataframe()[['wse']]
        except Exception as e:
            raise ValueError(f'River ID {river_id} not found in the SFDC table') from e


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
    metadata_table_path = get_uri('metadata_table')
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
