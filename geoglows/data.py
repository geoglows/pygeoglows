import json
import os
import pickle
from collections import OrderedDict
from io import StringIO

import pandas as pd
import requests
from shapely.geometry import Point, MultiPoint, shape
from shapely.ops import nearest_points

ENDPOINT = 'https://geoglows.ecmwf.int/api'

__all__ = ['forecast_stats', 'forecast_ensembles', 'forecast_warnings', 'forecast_records', 'historical',
           'daily_averages', 'monthly_averages', 'return_periods', 'available_data', 'available_dates',
           'available_regions', 'reach_to_region', 'reach_to_latlon', 'latlon_to_reach', 'latlon_to_region', ]


def forecast(reach_id: int, return_format: str = 'csv', endpoint: str = ENDPOINT,
                   s: requests.Session = False, **kwargs) -> pd.DataFrame or dict or str:
    """
        Retrieves statistics that summarize the ensemble streamflow forecast for a certain reach_id

        Args:
            reach_id: the ID of a stream
            return_format (str): 'csv', 'json', 'url'
            endpoint: the endpoint of an api instance
            s: requests.Session instance connected to the api's root url

        Keyword Args:
            date (str): a string specifying the date to request in YYYYMMDD format
            units (str): either "cms" (cubic meters per second, default) or "cfs" (cubic feet per second)

        Return Format:
            - return_format='csv' returns a pd.DataFrame()
            - return_format='json' returns a json
            - return_format='url' returns a url string for the rest query

        Example:
            .. code-block:: python
            
            geoglows.data.forecast_stats(12341234)
    """

    product = 'Forecast'
    url = f'{endpoint}/v2/{product}/{reach_id}'
    return _request(url, return_format, product, s, kwargs)


def forecast_stats(reach_id: int, return_format: str = 'csv', endpoint: str = ENDPOINT,
                   s: requests.Session = False, **kwargs) -> pd.DataFrame or dict or str:
    """
        Retrieves statistics that summarize the ensemble streamflow forecast for a certain reach_id

        Args:
            reach_id: the ID of a stream
            return_format (str): 'csv', 'json', 'url'
            endpoint: the endpoint of an api instance
            s: requests.Session instance connected to the api's root url

        Keyword Args:
            date (str): a string specifying the date to request in YYYYMMDD format
            units (str): either "cms" (cubic meters per second, default) or "cfs" (cubic feet per second)

        Return Format:
            - return_format='csv' returns a pd.DataFrame()
            - return_format='json' returns a json
            - return_format='url' returns a url string for the rest query

        Example:
            .. code-block:: python

            geoglows.data.forecast_stats(12341234)
    """

    product = 'ForecastStats'
    url = f'{endpoint}/v2/{product}/{reach_id}'
    return _request(url, return_format, product, s, kwargs)


def forecast_ensembles(reach_id: int, return_format: str = 'csv', endpoint: str = ENDPOINT,
                       s: requests.Session = False, **kwargs) -> pd.DataFrame or dict or str:
    """
    Retrieves each ensemble from the most recent streamflow forecast for a certain reach_id

    Args:
        reach_id: the ID of a stream
        return_format: 'csv', 'json', 'waterml', 'url'
        forecast_date: a string specifying the date to request in YYYYMMDD format
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='url' returns a url string for the rest query

    Example:
        .. code-block:: python

            data = geoglows.streamflow.forecast_ensembles(12341234)
    """
    product = 'ForecastEnsembles'
    url = f'{endpoint}/v2/{product}/{reach_id}'
    return _request(url, return_format, product, s, kwargs)


def forecast_warnings(region: str, return_format: str = 'csv', endpoint: str = ENDPOINT,
                      s: requests.Session = False) -> pd.DataFrame or dict or str:
    """
    Retrieves a csv listing streams likely to experience a return period level flow during the forecast period.

    Args:
        region: the name of a region as shown in the available_regions request
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='url' returns a url string for the rest query

    Example:
        .. code-block:: python

            data = geoglows.streamflow.forecast_warnings('australia-geoglows')
    """
    product = 'ForecastWarnings'
    url = f'{endpoint}/v2/{product}/'
    return _request(url, return_format, product, s, {'region': region})


def forecast_records(reach_id: int, return_format: str = 'csv', endpoint: str = ENDPOINT,
                     s: requests.Session = False, **kwargs) -> pd.DataFrame or dict or str:
    """
    Retrieves a csv showing the ensemble average forecasted flow for the year from January 1 to the current date

    Args:
        reach_id: the ID of a stream
        return_format: 'csv', 'json', 'waterml', 'url'
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Keyword Args:
        start_date: a string specifying the earliest date to request in YYYYMMDD format
        end_date: a string specifying the latest date to request in YYYYMMDD format

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='url' returns a url string for the rest query

    Example:
        .. code-block:: python

            data = geoglows.streamflow.forecast_warnings('australia-geoglows')
    """
    product = 'ForecastRecords'
    url = f'{endpoint}/v2/{product}/{reach_id}'
    return _request(url, return_format, product, s, kwargs)


def available_dates(reach_id: int = None, region: str = None, return_format: str = 'json',
                    endpoint: str = ENDPOINT, s: requests.Session = False) -> dict or str:
    """
    Retrieves the list of dates of stored streamflow forecasts. You need to specify either a reach_id or a region.

    Args:
        reach_id: the ID of a stream
        region: the name of a hydrologic region used in the model
        endpoint: the endpoint of an api instance
        return_format: 'json' or 'url'
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='json' *(default)* returns {'available_dates': ['list_of_dates', ]}
        - return_format='url' returns a url string for the rest query

    Example:
        .. code-block:: python

            data = geoglows.streamflow.available_dates(12341234)
    """
    product = 'AvailableDates'
    url = f'{endpoint}/v2/{product}/{reach_id}'
    return _request(url, return_format, product, s, kwargs)


def historical(reach_id: int, return_format: str = 'csv', endpoint: str = ENDPOINT,
               s: requests.Session = False, **kwargs) -> pd.DataFrame or dict or str:
    """
    Retrieves a historical streamflow simulation derived from a specified forcing for a certain reach_id

    Args:
        reach_id: the ID of a stream
        return_format: 'csv', 'json', 'url'
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='url' returns a url string for the rest query

    Example:
        .. code-block:: python

            data = geoglows.streamflow.historic_simulation(12341234)
    """
    product = 'Historical'
    url = f'{endpoint}/v2/{product}/{reach_id}'
    return _request(url, return_format, product, s, kwargs)


def daily_averages(reach_id: int, return_format: str = 'csv', endpoint: str = ENDPOINT,
                   s: requests.Session = False, **kwargs) -> pd.DataFrame or dict or str:
    """
    Retrieves the average flow for every day of the year at a certain reach_id.

    Args:
        reach_id: the ID of a stream
        return_format: 'csv', 'json', 'waterml', 'url'
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='url' returns a url string for the rest query

    Example:
        .. code-block:: python

            data = geoglows.streamflow.seasonal_average(12341234)
    """
    product = 'DailyAverages'
    url = f'{endpoint}/v2/{product}/{reach_id}'
    return _request(url, return_format, product, s, kwargs)


def monthly_averages(reach_id: int, return_format: str = 'csv', endpoint: str = ENDPOINT,
                     s: requests.Session = False, **kwargs) -> pd.DataFrame or dict or str:
    """
    Retrieves the average flow for each month at a certain reach_id.

    Args:
        reach_id: the ID of a stream
        return_format: 'csv', 'json', 'waterml', 'url'
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='url' returns a url string for the rest query

    Example:
        .. code-block:: python

            data = geoglows.streamflow.seasonal_average(12341234)
    """
    product = 'MonthlyAverages'
    url = f'{endpoint}/v2/{product}/{reach_id}'
    return _request(url, return_format, product, s, kwargs)


def return_periods(reach_id: int, return_format='csv', forcing='era_5',
                   endpoint=ENDPOINT, s: requests.Session = False) -> pd.DataFrame:
    """
    Retrieves the return period thresholds based on a specified historic simulation forcing on a certain reach_id.

    Args:
        reach_id: the ID of a stream
        forcing: the runoff dataset used to drive the historic simulation (era_interim or era_5)
        return_format: 'csv', 'json', 'waterml', 'url'
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='url' returns a url string for the rest query

    Example:
        .. code-block:: python

            data = geoglows.streamflow.return_periods(12341234)
    """
    product = 'ReturnPeriods/'
    url = f'{endpoint}/v2/{product}/{reach_id}'
    return _request(url, return_format, product, s, kwargs)


def available_data(endpoint: str = ENDPOINT, return_format='json', s: requests.Session = False) -> dict or str:
    """
    Returns a dictionary with a key for each available_regions containing the available_dates for that region

    Args:
        endpoint: the endpoint of an api instance
        return_format: 'json' or 'url'
        s: requests.Session instance connected to the api's root url

    Returns:
        dict

    Example:
        .. code-block:: python

            data = geoglows.streamflow.available_data()

    """
    product = 'AvailableData'
    url = f'{endpoint}/v2/{product}/'
    return _request(url, return_format, product, s, {})


def available_regions(endpoint: str = ENDPOINT, return_format='json', s: requests.Session = False) -> dict or str:
    """
    Retrieves a list of regions available at the endpoint

    Args:
        endpoint: the endpoint of an api instance
        return_format: 'json' or 'url'
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='json' *(default)* returns {'available_regions': ['list_of_dates']}
        - return_format='url' returns a url string for the rest query

    Example:
        .. code-block:: python

            data = geoglows.streamflow.available_regions(12341234)
    """
    product = 'AvailableRegions'
    url = f'{endpoint}/v2/{product}/'
    return _request(url, return_format, product, s, {})


# UTILITY FUNCTIONS
def reach_to_region(reach_id: int) -> str:
    """
    returns the delineation region name corresponding to the range of numbers for a given reach_id.
    does not validate that the reach_id exists in the region, just associates a number to a name.

    Args:
        reach_id: the ID for a stream

    Return:
        the name of the delineated world region used by the API.

    Example:
        region = geoglows.streamflow.reach_to_region(5000000)
    """
    # Indonesia 1M's
    # ------australia 2M (currently 200k's)
    # Japan 3M's
    # East Asia 4M's
    # South Asia 5M's
    # ------middle_east 6M (currently 600k's)
    # Africa 7M's
    # Central Asia 8M's
    # South America 9M's
    # West Asia 10M's
    # -------central_america 11M (currently 900k's)
    # Europe 12M's
    # North America 13M's

    if not isinstance(reach_id, int):
        reach_id = int(reach_id)

    lookup = OrderedDict([
        # IMPROPERLY NUMBERED REGIONS
        ('australia-geoglows', 300000),
        ('middle_east-geoglows', 700000),
        ('central_america-geoglows', 1000000),
        # CORRECTLY NUMBERED REGIONS
        ('islands-geoglows', 2000000),
        ('japan-geoglows', 4000000),
        ('east_asia-geoglows', 5000000),
        ('south_asia-geoglows', 6000000),
        ('africa-geoglows', 8000000),
        ('central_asia-geoglows', 9000000),
        ('south_america-geoglows', 10000000),
        ('west_asia-geoglows', 11000000),
        ('europe-geoglows', 13000000),
        ('north_america-geoglows', 14000000)
    ])
    for region, threshold in lookup.items():
        if reach_id < threshold:
            return region
    raise ValueError(f'{reach_id} not in the range of reach_ids for this model')


def reach_to_latlon(reach_id: int, region: str = False) -> tuple:
    """
    Finds the latitude and longitude of the centroid of the stream with the specified reach_id. Does not validate that
    the reach_id exists, but it will raise an error if the reach_id does not exist

    Args:
        reach_id: the ID for a stream
        region: if known, you can specify the region of your reach_id

    Returns:
        tuple(latitude, longitude)
    """
    if not region:
        region = reach_to_region(reach_id)
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'geometry'))
    df = pd.read_pickle(os.path.join(base_path, f'{region}-comid_lat_lon_z.pickle'))
    df = df[df.index == reach_id]
    if len(df.index) == 0:
        raise LookupError(f'The reach_id "{reach_id}" was not found in region "{region}"')
    return float(df['Lat'].values[0]), float(df['Lon'].values[0])


def latlon_to_reach(lat: float, lon: float) -> dict:
    """
    Uses a list of lat/lon for each reach_id to find the closest stream reach to a given lat/lon location

    Args:
        lat: a valid latitude
        lon: a valid longitude

    Return:
        a dictionary containing the reach_id as well as the name of the region and the distance
        from the provided lat and lon to the stream in units of degrees.
    """
    if lat is False or lon is False:
        raise ValueError('provide a valid latitude and longitude to in order to find a reach_id')

    # determine the region that the point is in
    region = latlon_to_region(lat, lon)

    # switch the point because the csv's are lat/lon, backwards from what shapely expects (lon then lat)
    point = Point(float(lat), float(lon))

    # open the region csv
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'geometry'))
    df = pd.read_pickle(os.path.join(base_path, f'{region}-geoglows-comid_lat_lon_z.pickle'))
    points_df = df.loc[:, "Lat":"Lon"].apply(Point, axis=1)

    # determine which point is closest
    multi_pt = MultiPoint(points_df.tolist())
    nearest_pt = nearest_points(point, multi_pt)
    reach_id = int(points_df[points_df == nearest_pt[1]].index[0])
    distance = nearest_pt[0].distance(nearest_pt[1])

    # if the nearest stream if more than .1 degrees away, you probably didn't find the right stream
    if distance > 0.11:
        return {"error": "Nearest river is more than ~10km away."}
    else:
        return dict(reach_id=reach_id, region=region, distance=distance)


def latlon_to_region(lat: float, lon: float) -> str:
    """
    Uses a the bounding boxes of each region to determine which contains the given lat/lon

    Args:
        lat: a valid latitude
        lon: a valid longitude

    Return:
        the name of a region
    """
    if lat is False or lon is False:
        raise ValueError('provide a valid latitude and longitude to in order to find a region')

    # open the bounding boxes csv, figure out which regions the point lies within
    point = Point(float(lon), float(lat))
    bounds_pickle = os.path.abspath(os.path.join(os.path.dirname(__file__), 'geometry', 'boundaries.pickle'))
    with open(bounds_pickle, 'rb') as f:
        region_bounds = json.loads(pickle.load(f))
    for region in region_bounds:
        for polygon in region_bounds[region]['features']:
            if shape(polygon['geometry']).contains(point):
                return region
    # if there weren't any regions, return that there was an error
    raise ValueError('This point is not within any of the supported delineation regions.')


# API AUXILIARY FUNCTION
def _request(endpoint: str, return_format: str, product: str, s: requests.Session, passed_kwargs):
    if return_format == 'url':
        return endpoint

    # request the data from the API
    if s:
        data = s.get(endpoint, params=passed_kwargs)
    else:
        data = requests.get(endpoint, params=passed_kwargs)
    if data.status_code != 200:
        raise RuntimeError('Received an error from the Streamflow REST API: ' + data.text)

    # process the response from the API as appropriate to make the corresponding python object
    if return_format == 'csv':
        tmp = pd.read_csv(StringIO(data.text), index_col=0)
        if 'z' in tmp.columns:
            del tmp['z']
        if product in ('ForecastWarnings/', 'ReturnPeriods/', 'DailyAverages/', 'MonthlyAverages/'):
            return tmp
        if product == 'SeasonalAverage/':
            tmp.index = pd.to_datetime(tmp.index + 1, format='%j').strftime('%b %d')
            return tmp
        tmp.index = pd.to_datetime(tmp.index)
        return tmp
    elif return_format == 'json':
        return json.loads(data.text)
    else:
        raise ValueError(f'Unsupported return format requested: {return_format}')


forecast_stats(3000150, keyarg=1)
