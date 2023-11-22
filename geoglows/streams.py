import os
import warnings

import pandas as pd

from .data import master_table

__all__ = ['reach_to_vpu', 'latlon_to_reach', 'reach_to_latlon', ]

GEOGLOWS_MASTER_TABLE_LOCAL_PATH = os.path.join(os.path.dirname(__file__), 'data', 'geoglows-v2-master-table.parquet')


def _read_master_table() -> pd.DataFrame:
    """
    Read the master table from the local data directory
    """
    warn = """
    Local copy of geoglows v2 master table not found.
    Please download the master table from S3 and place it in the data directory.
    Attempting to fetch a copy from S3 to cache locally.
    """
    if not os.path.exists(GEOGLOWS_MASTER_TABLE_LOCAL_PATH):
        warnings.warn(warn)
        df = master_table(columns=['TDXHydroLinkNo', 'VPUCode', 'lat', 'lon'])
        df.to_parquet(GEOGLOWS_MASTER_TABLE_LOCAL_PATH)
        return df
    return pd.read_parquet(GEOGLOWS_MASTER_TABLE_LOCAL_PATH)


def reach_to_vpu(reach_id: int) -> str or int:
    return (
        _read_master_table()
        .loc[lambda x: x['TDXHydroLinkNo'] == reach_id, 'VPUCode']
        .values[0]
    )


def latlon_to_reach(lat: float, lon: float) -> int:
    df = _read_master_table()
    df['dist'] = ((df['lat'] - lat) ** 2 + (df['lon'] - lon) ** 2) ** 0.5
    return df.loc[lambda x: x['dist'] == df['dist'].min(), 'TDXHydroLinkNo'].values[0]


def reach_to_latlon(reach_id: int) -> tuple:
    return (
        _read_master_table()
        .loc[lambda x: x['TDXHydroLinkNo'] == reach_id, ['lat', 'lon']]
        .values[0]
    )
