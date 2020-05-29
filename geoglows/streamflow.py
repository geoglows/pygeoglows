import json
import os
import pickle
import warnings
from collections import OrderedDict
from io import StringIO

import pandas as pd
import requests
from shapely.geometry import Point, MultiPoint, shape
from shapely.ops import nearest_points

__all__ = ['forecast_stats', 'forecast_ensembles', 'forecast_warnings', 'forecast_records', 'historic_simulation',
           'seasonal_average', 'return_periods', 'available_data', 'available_dates', 'available_regions',
           'reach_to_region', 'reach_to_latlon', 'latlon_to_reach', 'latlon_to_region']

ENDPOINT = 'https://tethys2.byu.edu/localsptapi/api/'
AZURE_ENDPOINT = 'http://gsf-api-vm.eastus.cloudapp.azure.com/api/'
BYU_ENDPOINT = 'https://tethys2.byu.edu/localsptapi/api/'
LOCAL_ENDPOINT = 'http://0.0.0.0:8090/api/'


# FUNCTIONS THAT CALL THE GLOBAL STREAMFLOW PREDICTION API
def forecast_stats(reach_id: int, endpoint=ENDPOINT, return_format='csv', **kwargs):
    """
    Retrieves statistics that summarize the most recent streamflow forecast for a certain reach_id

    Args:
        reach_id: the ID of a stream
        endpoint: the endpoint of an api instance
        return_format: 'csv', 'json', 'waterml', 'request', 'url'

    Keyword Args:
        lat, lon: the lat/lon where you want streamflow for when reach_id is not known. Must provide both lat and lon.

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='request' returns a request response object
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = geoglows.streamflow.forecast_stats(12341234)
    """
    method = 'ForecastStats/'

    # handle the lat and lon inputs if you don't have the reach_id
    if not reach_id:
        reach_id = latlon_to_reach(kwargs.get('lat', False), kwargs.get('lon', False))['reach_id']

    # if you only wanted the url, quit here
    if return_format == 'url':
        return endpoint + method + '?reach_id={0}'.format(reach_id)

    # return the requested data
    return _make_request(endpoint, method, {'reach_id': reach_id, 'return_format': return_format}, return_format)


def forecast_ensembles(reach_id: int, endpoint=ENDPOINT, return_format='csv', **kwargs):
    """
    Retrieves each ensemble from the most recent streamflow forecast for a certain reach_id

    Args:
        reach_id (int): the ID of a stream
        endpoint (str): the endpoint of an api instance
        return_format (str): 'csv', 'json', 'waterml', 'request', 'url'

    Keyword Args:
        lat, lon: the lat/lon where you want streamflow for when reach_id is not known. Must provide both lat and lon.

    Return Format:
        - return_format='csv' returns a pandas dataframe
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='request' returns a request response object
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = geoglows.streamflow.forecast_ensembles(12341234)
    """
    method = 'ForecastEnsembles/'

    # handle the lat and lon inputs if you don't have the reach_id
    if not reach_id:
        reach_id = latlon_to_reach(kwargs.get('lat', False), kwargs.get('lon', False))['reach_id']

    # if you only wanted the url, quit here
    if return_format == 'url':
        return endpoint + method + '?reach_id={0}'.format(reach_id)

    # return the requested data
    return _make_request(endpoint, method, {'reach_id': reach_id, 'return_format': return_format}, return_format)


def forecast_warnings(region: str, endpoint=ENDPOINT, return_format='csv', **kwargs):
    """
    Retrieves a csv listing streams likely to experience a return period level flow during the forecast period.

    Args:
        region: the name of a region as shown in the available_regions request
        endpoint: the endpoint of an api instance
        return_format: 'csv', 'json', 'waterml', 'request', 'url'

    Keyword Args:
        lat, lon: the lat/lon of an area you want to retrieve warnings for

    Return Format:
        - return_format='csv' returns a pandas dataframe
        - return_format='request' returns a request response object
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = geoglows.streamflow.forecast_warnings('australia-geoglows')
    """
    method = 'ForecastWarnings/'

    # handle the lat and lon inputs if you don't have the reach_id
    if not region:
        region = latlon_to_region(kwargs.get('lat', False), kwargs.get('lon', False))

    # if you only wanted the url, quit here
    if return_format == 'url':
        return endpoint + method + '?region={0}'.format(region)

    # return the requested data
    return _make_request(endpoint, method, {'region': region, 'return_format': return_format}, return_format)


def forecast_records(reach_id: int, endpoint=ENDPOINT, return_format='csv', **kwargs):
    """
    Retrieves a csv listing streams likely to experience a return period level flow during the forecast period.

    Args:
        reach_id: the ID of a stream
        endpoint: the endpoint of an api instance
        return_format (str): 'csv', 'json', 'waterml', 'request', 'url'

    Keyword Args:
        lat, lon: the lat/lon where you want streamflow for when reach_id is not known. Must provide both lat and lon.

    Return Format:
        - return_format='csv' returns a pandas dataframe
        - return_format='request' returns a request response object
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = geoglows.streamflow.forecast_warnings('australia-geoglows')
    """
    method = 'ForecastRecords/'

    # handle the lat and lon inputs if you don't have the reach_id
    if not reach_id:
        reach_id = latlon_to_reach(kwargs.get('lat', False), kwargs.get('lon', False))['reach_id']

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}'

    # return the requested data
    return _make_request(endpoint, method, {'reach_id': reach_id, 'return_format': return_format}, return_format)


def historic_simulation(reach_id: int, forcing='era_5', endpoint=ENDPOINT, return_format='csv', **kwargs):
    """
    Retrieves a historical streamflow simulation derived from a specified forcing for a certain reach_id

    Args:
        reach_id: the ID of a stream
        forcing: the runoff dataset used to drive the historic simulation (era_interim or era_5)
        endpoint: the endpoint of an api instance
        return_format: 'csv', 'json', 'waterml', 'request', 'url'

    Keyword Args:
        lat, lon: the lat/lon where you want streamflow for when reach_id is not known. Must provide both lat and lon.

    Return Format:
        - return_format='csv' returns a pandas dataframe
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='request' returns a request response object
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = geoglows.streamflow.historic_simulation(12341234)
    """
    method = 'HistoricSimulation/'

    # handle the lat and lon inputs if you don't have the reach_id
    if not reach_id:
        reach_id = latlon_to_reach(kwargs.get('lat', False), kwargs.get('lon', False))['reach_id']

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}&forcing={forcing}'

    # return the requested data
    params = {'reach_id': reach_id, 'forcing': forcing, 'return_format': return_format}
    return _make_request(endpoint, method, params, return_format)


def seasonal_average(reach_id: int, forcing='era_5', endpoint=ENDPOINT, return_format='csv', **kwargs):
    """
    Retrieves the average flow for every day of the year at a certain reach_id.

    Args:
        reach_id: the ID of a stream
        forcing: the runoff dataset used to drive the historic simulation (era_interim or era_5)
        endpoint: the endpoint of an api instance
        return_format: 'csv', 'json', 'waterml', 'request', 'url'

    Keyword Args:
        lat, lon: the lat/lon where you want streamflow for when reach_id is not known. Must provide both lat and lon.

    Return Format:
        - return_format='csv' returns a pandas dataframe
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='request' returns a request response object
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = geoglows.streamflow.seasonal_average(12341234)
    """
    method = 'SeasonalAverage/'

    # handle the lat and lon inputs if you don't have the reach_id
    if not reach_id:
        reach_id = latlon_to_reach(kwargs.get('lat', False), kwargs.get('lon', False))['reach_id']

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}&forcing={forcing}'

    # return the requested data
    params = {'reach_id': reach_id, 'forcing': forcing, 'return_format': return_format}
    return _make_request(endpoint, method, params, return_format)


def return_periods(reach_id: int, forcing='era_5', endpoint=ENDPOINT, return_format='csv', **kwargs):
    """
    Retrieves the return period thresholds based on a specified historic simulation forcing on a certain reach_id.

    Args:
        reach_id: the ID of a stream
        forcing: the runoff dataset used to drive the historic simulation (era_interim or era_5)
        endpoint: the endpoint of an api instance
        return_format: 'csv', 'json', 'waterml', 'request', 'url'

    Keyword Args:
        lat, lon: the lat/lon where you want streamflow for when reach_id is not known. Must provide both lat and lon.

    Return Format:
        - return_format='csv' returns a pandas dataframe
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='request' returns a request response object
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = geoglows.streamflow.return_periods(12341234)
    """
    method = 'ReturnPeriods/'

    # handle the lat and lon inputs if you don't have the reach_id
    if not reach_id:
        reach_id = latlon_to_reach(kwargs.get('lat', False), kwargs.get('lon', False))['reach_id']

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}&forcing={forcing}'

    # return the requested data
    params = {'reach_id': reach_id, 'forcing': forcing, 'return_format': return_format}
    return _make_request(endpoint, method, params, return_format)


def available_data(endpoint=ENDPOINT, return_format='json') -> dict:
    """
    Returns a dictionary with a key for each available_regions containing the available_dates for that region

    Args:
        endpoint: the endpoint of an api instance
        return_format: 'json' or 'url'

    Returns:
        dict

    Example:
        .. code-block:: python

            data = geoglows.streamflow.available_data()

    """
    method = 'AvailableData/'

    # if you only wanted the url, quit here
    if return_format == 'url':
        return endpoint + method

    # return the requested data
    return _make_request(endpoint, method, {}, return_format)


def available_regions(endpoint=ENDPOINT, return_format='json'):
    """
    Retrieves a list of regions available at the endpoint

    Args:
        endpoint: the endpoint of an api instance
        return_format: 'json' or 'url'

    Return Format:
        - return_format='json' *(default)* returns {'available_regions': ['list_of_dates']}
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = geoglows.streamflow.available_regions(12341234)
    """
    method = 'AvailableRegions/'

    if return_format == 'url':
        return endpoint + method

    # return the requested data
    return _make_request(endpoint, method, {}, return_format)


def available_dates(reach_id=None, region=None, endpoint=ENDPOINT, return_format='json') -> dict:
    """
    Retrieves the list of dates of stored streamflow forecasts. You need to specify either a reach_id or a region.

    Args:
        reach_id: the ID of a stream
        region: the name of a hydrologic region used in the model
        endpoint: the endpoint of an api instance
        return_format: 'json' or 'url'

    Return Format:
        - return_format='json' *(default)* returns {'available_dates': ['list_of_dates']}
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = geoglows.streamflow.available_dates(12341234)
    """
    method = 'AvailableDates/'

    # you need a region for the api call, so the user needs to provide one or a valid reach_id to get it from
    if region:
        params = {'region': region}
    elif reach_id:
        params = {'region': reach_to_region(reach_id)}
    else:
        raise RuntimeError('specify a region or a reach_id')

    # if you only wanted the url, quit here
    if return_format == 'url':
        return endpoint + method

    # return the requested data
    return _make_request(endpoint, method, params, return_format)


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
def _make_request(endpoint: str, method: str, params: dict, return_format: str):
    if return_format == 'request':
        params['return_format'] == 'csv'

    # request the data from the API
    data = requests.get(endpoint + method, params=params)
    if data.status_code != 200:
        warnings.warn('Recieved an error from the Streamflow REST API: ' + data.text)
        raise RuntimeError('Unable to retrieve information from the Streamflow REST API')

    # process the response from the API as appropriate to make the corresponding python object
    if return_format == 'csv':
        if method == 'ForecastWarnings/' or method == 'ReturnPeriods/':
            return pd.read_csv(StringIO(data.text), index_col=0)
        if method == 'SeasonalAverage/':
            tmp = pd.read_csv(StringIO(data.text), index_col='day_of_year')
            tmp.index = pd.to_datetime(tmp.index + 1, format='%j').strftime('%b %d')
            return tmp
        tmp = pd.read_csv(StringIO(data.text), index_col='datetime')
        tmp.index = pd.to_datetime(tmp.index)
        if 'z' in tmp.columns:
            del tmp['z']
        return tmp
    elif return_format == 'json':
        return json.loads(data.text)
    elif return_format == 'waterml':
        return data.text
    elif return_format == 'request':
        return data
    else:
        raise ValueError('Unsupported return format requested: ' + str(return_format))
