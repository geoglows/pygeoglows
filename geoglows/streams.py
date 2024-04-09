import numpy as np

from .data import metadata_tables

__all__ = ['reach_to_vpu', 'latlon_to_reach', 'reach_to_latlon', ]


def reach_to_vpu(reach_id: int) -> str or int:
    return (
        metadata_tables(columns=['LINKNO', 'VPUCode'])
        .loc[lambda x: x['LINKNO'] == reach_id, 'VPUCode']
        .values[0]
    )


def latlon_to_reach(lat: float, lon: float) -> int:
    df = metadata_tables(columns=['LINKNO', 'lat', 'lon'])
    df['dist'] = ((df['lat'] - lat) ** 2 + (df['lon'] - lon) ** 2) ** 0.5
    return df.loc[lambda x: x['dist'] == df['dist'].min(), 'LINKNO'].values[0]


def reach_to_latlon(reach_id: int) -> np.ndarray:
    return (
        metadata_tables(columns=['LINKNO', 'lat', 'lon'])
        .loc[lambda x: x['LINKNO'] == reach_id, ['lat', 'lon']]
        .values[0]
    )
