import numpy as np

from .data import metadata_tables

__all__ = ['river_to_vpu', 'latlon_to_river', 'river_to_latlon', ]


def river_to_vpu(river_id: int) -> int:
    """
    Gives the VPU number for a given River ID number

    Args:
        river_id (int): a 9 digit integer that is a valid GEOGLOWS River ID number

    Returns:
        int: a 3 digit integer that is the VPU number for the given River ID number
    """
    return (
        metadata_tables(columns=['LINKNO', 'VPUCode'])
        .loc[lambda x: x['LINKNO'] == river_id, 'VPUCode']
        .values[0]
    )


def latlon_to_river(lat: float, lon: float) -> int:
    """
    Gives the River ID number whose outlet is nearest the given lat and lon
    Args:
        lat (float): a latitude
        lon (float): a longitude

    Returns:
        int: a 9 digit integer that is a valid GEOGLOWS River ID number
    """
    df = metadata_tables(columns=['LINKNO', 'lat', 'lon'])
    df['dist'] = ((df['lat'] - lat) ** 2 + (df['lon'] - lon) ** 2) ** 0.5
    return df.loc[lambda x: x['dist'] == df['dist'].min(), 'LINKNO'].values[0]


def river_to_latlon(river_id: int) -> np.ndarray:
    """
    Gives the lat and lon of the outlet of the river with the given River ID number

    Args:
        river_id (int): a 9 digit integer that is a valid GEOGLOWS River ID number

    Returns:
        np.ndarray: a numpy array of floats, [lat, lon]
    """
    return (
        metadata_tables(columns=['LINKNO', 'lat', 'lon'])
        .loc[lambda x: x['LINKNO'] == river_id, ['lat', 'lon']]
        .values[0]
    )
