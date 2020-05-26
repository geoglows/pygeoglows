import datetime
import json
import os
import pickle
from collections import OrderedDict
from io import StringIO

import jinja2
import pandas
import pandas as pd
import plotly.graph_objs as go
import requests
import scipy.stats
from plotly.offline import plot as offline_plot
from shapely.geometry import Point, MultiPoint, shape
from shapely.ops import nearest_points

__all__ = ['forecast_stats', 'forecast_ensembles', 'forecast_warnings', 'forecast_records', 'historic_simulation',
           'seasonal_average', 'return_periods', 'available_data', 'available_dates', 'available_regions',
           'hydroviewer_plot', 'forecast_plot', 'records_plot', 'ensembles_plot', 'historical_plot', 'seasonal_plot',
           'flow_duration_curve_plot', 'probabilities_table', 'return_periods_table', 'reach_to_region',
           'latlon_to_reach']

BYU_ENDPOINT = 'https://tethys2.byu.edu/localsptapi/api/'
AZURE_HOST = 'http://gsf-api-vm.eastus.cloudapp.azure.com/api/'


# FUNCTIONS THAT CALL THE GLOBAL STREAMFLOW PREDICTION API
def forecast_stats(reach_id: int, endpoint=BYU_ENDPOINT, return_format='csv', **kwargs):
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


def forecast_ensembles(reach_id: int, endpoint=BYU_ENDPOINT, return_format='csv', **kwargs):
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


def forecast_warnings(region: str, endpoint=BYU_ENDPOINT, return_format='csv', **kwargs):
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


def forecast_records(reach_id: int, endpoint=BYU_ENDPOINT, return_format='csv', **kwargs):
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
        return endpoint + method + '?reach_id={0}'.format(reach_id)

    # return the requested data
    return _make_request(endpoint, method, {'reach_id': reach_id, 'return_format': return_format}, return_format)


def historic_simulation(reach_id: int, forcing='era_5', endpoint=BYU_ENDPOINT, return_format='csv', **kwargs):
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
        return endpoint + method + '?reach_id={0}&forcing={1}'.format(reach_id, forcing, return_format)

    # return the requested data
    params = {'reach_id': reach_id, 'forcing': forcing, 'return_format': return_format}
    return _make_request(endpoint, method, params, return_format)


def seasonal_average(reach_id: int, forcing='era_5', endpoint=BYU_ENDPOINT, return_format='csv', **kwargs):
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
        return endpoint + method + '?reach_id={0}&forcing={1}'.format(reach_id, forcing, return_format)

    # return the requested data
    params = {'reach_id': reach_id, 'forcing': forcing, 'return_format': return_format}
    return _make_request(endpoint, method, params, return_format)


def return_periods(reach_id: int, forcing='era_5', endpoint=BYU_ENDPOINT, return_format='csv', **kwargs):
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
        return endpoint + method + '?reach_id={0}&forcing={1}'.format(reach_id, forcing, return_format)

    # return the requested data
    params = {'reach_id': reach_id, 'forcing': forcing, 'return_format': return_format}
    return _make_request(endpoint, method, params, return_format)


def available_data(endpoint=BYU_ENDPOINT, return_format='json') -> dict:
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


def available_regions(endpoint=BYU_ENDPOINT, return_format='json'):
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


def available_dates(reach_id=None, region=None, endpoint=BYU_ENDPOINT, return_format='json') -> dict:
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
    return None


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


# FUNCTIONS THAT PROCESS THE RESULTS OF THE API INTO A PLOTLY PLOT OR DICTIONARY
def hydroviewer_plot(records: pd.DataFrame, stats: pd.DataFrame, rperiods: pd.DataFrame = None, **kwargs):
    """
    Creates the standard plot for a hydroviewer

    Args:
        records: the response from forecast_records
        stats: the response from forecast_stats
        rperiods: the response from return_periods

    Keyword Args:
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        reach_id: the reach ID of COMID of a stream to be added to the plot title
        drain_area: a string containing the area and units of the area upstream of this reach that will be shown on the
            plot title
        record_days_len: the number of days of forecast records to show before the start of the forecast (if available)

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.hydroviewer_plot(records, stats, rperiods)
    """
    # Process supported key word arguments (kwargs)
    reach_id = kwargs.get('reach_id', None)
    drain_area = kwargs.get('drain_area', None)
    outformat = kwargs.get('outformat', 'plotly')
    rec_day = kwargs.get('record_days_len', 7)

    # Validate a few of the important inputs
    if not isinstance(records, pd.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or html')

    # limit the forecast records to 7 days before the start of the forecast
    records = records.loc[records.index >= pd.to_datetime(datetime.date.today() - datetime.timedelta(days=rec_day))]

    # Start processing the inputs
    records_dates = records.index.tolist()
    dates = stats.index.tolist()
    startdate = min(records_dates[0], dates[0])
    enddate = max(records_dates[-1], dates[-1])

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_ensembles': stats['mean (m^3/s)'].dropna(axis=0).index.tolist(),
        'x_hires': stats['mean (m^3/s)'].dropna(axis=0).index.tolist(),
        'x_records': records_dates,
        'recorded_flows': records['streamflow (m^3/s)'].dropna(axis=0).tolist(),
        'y_max': max(stats['max (m^3/s)']),
        'min': list(stats['min (m^3/s)'].dropna(axis=0)),
        'mean': list(stats['mean (m^3/s)'].dropna(axis=0)),
        'max': list(stats['max (m^3/s)'].dropna(axis=0)),
        'stdlow': list(stats['std_dev_range_lower (m^3/s)'].dropna(axis=0)),
        'stdup': list(stats['std_dev_range_upper (m^3/s)'].dropna(axis=0)),
        'hires': list(stats['high_res (m^3/s)'].dropna(axis=0)),
    }
    if rperiods is not None:
        plot_data['r2']: rperiods['return_period_2'].values[0]
        plot_data['r5']: rperiods['return_period_5'].values[0]
        plot_data['r10']: rperiods['return_period_10'].values[0]
        plot_data['r25']: rperiods['return_period_25'].values[0]
        plot_data['r50']: rperiods['return_period_50'].values[0]
        plot_data['r100']: rperiods['return_period_100'].values[0]
        shapes = _rperiod_shapes(startdate, enddate, rperiods, plot_data['y_max'])
    else:
        shapes = []

    if outformat == 'json':
        return plot_data

    recorded_flows = go.Scatter(
        name='1st day forecasted flows',
        x=plot_data['x_records'],
        y=plot_data['recorded_flows'],
        line=dict(color='orange'),
    )
    meanplot = go.Scatter(
        name='Mean',
        x=plot_data['x_ensembles'],
        y=plot_data['mean'],
        line=dict(color='blue'),
    )
    maxplot = go.Scatter(
        name='Max',
        x=plot_data['x_ensembles'],
        y=plot_data['max'],
        fill='tonexty',
        mode='lines',
        line=dict(color='rgb(152, 251, 152)', width=0)
    )
    minplot = go.Scatter(
        name='Min',
        x=plot_data['x_ensembles'],
        y=plot_data['min'],
        fill=None,
        mode='lines',
        line=dict(color='rgb(152, 251, 152)')
    )
    stdlowplot = go.Scatter(
        name='Std. Dev. Lower',
        x=plot_data['x_ensembles'],
        y=plot_data['stdlow'],
        fill='tonexty',
        mode='lines',
        line=dict(color='rgb(152, 251, 152)', width=0)
    )
    stdupplot = go.Scatter(
        name='Std. Dev. Upper',
        x=plot_data['x_ensembles'],
        y=plot_data['stdup'],
        fill='tonexty',
        mode='lines',
        line={'width': 0, 'color': 'rgb(34, 139, 34)'}
    )
    hires = go.Scatter(
        name='Higher Resolution',
        x=plot_data['x_hires'],
        y=plot_data['hires'],
        line={'color': 'black'}
    )
    layout = go.Layout(
        title=__build_title('Forecasted Streamflow', reach_id, drain_area),
        xaxis={'title': 'Date'},
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * plot_data['y_max']]
        },
        shapes=shapes
    )
    figure = go.Figure([recorded_flows, minplot, stdlowplot, stdupplot, maxplot, meanplot, hires], layout=layout)
    if outformat == 'plotly':
        return figure
    if outformat == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    return


def forecast_plot(stats: pd.DataFrame, rperiods: pd.DataFrame = None, **kwargs):
    """
    Makes the streamflow data and optional metadata into a plotly plot

    Args:
        stats: the csv response from forecast_stats
        rperiods: the csv response from return_periods

    Keyword Args:
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        reach_id: the reach ID of COMID of a stream to be added to the plot title
        drain_area: a string containing the area and units of the area upstream of this reach that will be shown on the
            plot title

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.forecast_plot(stats, rperiods)
    """
    # Process supported key word arguments (kwargs)
    reach_id = kwargs.get('reach_id', None)
    drain_area = kwargs.get('drain_area', None)
    outformat = kwargs.get('outformat', 'plotly')

    # Validate a few of the important inputs
    if not isinstance(stats, pd.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or html')

    # Start processing the inputs
    dates = stats.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_ensembles': stats['mean (m^3/s)'].dropna(axis=0).index.tolist(),
        'x_hires': stats['mean (m^3/s)'].dropna(axis=0).index.tolist(),
        'y_max': max(stats['max (m^3/s)']),
        'min': list(stats['min (m^3/s)'].dropna(axis=0)),
        'mean': list(stats['mean (m^3/s)'].dropna(axis=0)),
        'max': list(stats['max (m^3/s)'].dropna(axis=0)),
        'stdlow': list(stats['std_dev_range_lower (m^3/s)'].dropna(axis=0)),
        'stdup': list(stats['std_dev_range_upper (m^3/s)'].dropna(axis=0)),
        'hires': list(stats['high_res (m^3/s)'].dropna(axis=0)),
    }
    if rperiods is not None:
        plot_data['r2']: rperiods['return_period_2'].values[0]
        plot_data['r5']: rperiods['return_period_5'].values[0]
        plot_data['r10']: rperiods['return_period_10'].values[0]
        plot_data['r25']: rperiods['return_period_25'].values[0]
        plot_data['r50']: rperiods['return_period_50'].values[0]
        plot_data['r100']: rperiods['return_period_100'].values[0]
        shapes = _rperiod_shapes(startdate, enddate, rperiods, plot_data['y_max'])
    else:
        shapes = []

    if outformat == 'json':
        return plot_data

    meanplot = go.Scatter(
        name='Mean',
        x=plot_data['x_ensembles'],
        y=plot_data['mean'],
        line=dict(color='blue'),
    )
    maxplot = go.Scatter(
        name='Max',
        x=plot_data['x_ensembles'],
        y=plot_data['max'],
        fill='tonexty',
        mode='lines',
        line=dict(color='rgb(152, 251, 152)', width=0)
    )
    minplot = go.Scatter(
        name='Min',
        x=plot_data['x_ensembles'],
        y=plot_data['min'],
        fill=None,
        mode='lines',
        line=dict(color='rgb(152, 251, 152)')
    )
    stdlowplot = go.Scatter(
        name='Std. Dev. Lower',
        x=plot_data['x_ensembles'],
        y=plot_data['stdlow'],
        fill='tonexty',
        mode='lines',
        line=dict(color='rgb(152, 251, 152)', width=0)
    )
    stdupplot = go.Scatter(
        name='Std. Dev. Upper',
        x=plot_data['x_ensembles'],
        y=plot_data['stdup'],
        fill='tonexty',
        mode='lines',
        line={'width': 0, 'color': 'rgb(34, 139, 34)'}
    )
    hires = go.Scatter(
        name='Higher Resolution',
        x=plot_data['x_hires'],
        y=plot_data['hires'],
        line={'color': 'black'}
    )
    layout = go.Layout(
        title=__build_title('Forecasted Streamflow', reach_id, drain_area),
        xaxis={'title': 'Date'},
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * plot_data['y_max']]
        },
        shapes=shapes
    )
    figure = go.Figure([minplot, stdlowplot, stdupplot, maxplot, meanplot, hires], layout=layout)
    if outformat == 'plotly':
        return figure
    if outformat == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    return


def ensembles_plot(ensembles: pd.DataFrame, rperiods: pd.DataFrame = None, **kwargs):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        ensembles: the csv response from forecast_ensembles
        rperiods: the csv response from return_periods

    Keyword Args
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        reach_id: the reach ID of COMID of a stream to be added to the plot title
        drain_area: a string containing the area and units of the area upstream of this reach that will
        be shown on the plot title

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.ensembles_plot(ensembles, rperiods)
    """
    # Process supported key word arguments (kwargs)
    reach_id = kwargs.get('reach_id', None)
    drain_area = kwargs.get('drain_area', None)
    outformat = kwargs.get('outformat', 'plotly')

    # Validate a few of the important inputs
    if not isinstance(ensembles, pd.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or html')

    # variables to determine the maximum flow and hold all the scatter plot lines
    max_flows = []
    scatters = []

    # determine the threshold values for return periods and the start/end dates so we can plot them
    dates = ensembles.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    # process the series' components and store them in a dictionary
    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_1-51': ensembles['ensemble_01 (m^3/s)'].dropna(axis=0).index.tolist(),
        'x_52': ensembles['ensemble_52 (m^3/s)'].dropna(axis=0).index.tolist(),
    }

    # add a dictionary entry for each of the ensemble members. the key for each series is the integer ensemble number
    for ensemble in ensembles.columns:
        plot_data[int(ensemble[9:11])] = ensembles[ensemble].dropna(axis=0).tolist()
        max_flows.append(max(plot_data[int(ensemble[9:11])]))
    plot_data['y_max'] = max(max_flows)

    if rperiods is not None:
        plot_data['r2']: rperiods['return_period_2'].values[0]
        plot_data['r5']: rperiods['return_period_5'].values[0]
        plot_data['r10']: rperiods['return_period_10'].values[0]
        plot_data['r25']: rperiods['return_period_25'].values[0]
        plot_data['r50']: rperiods['return_period_50'].values[0]
        plot_data['r100']: rperiods['return_period_100'].values[0]
        shapes = _rperiod_shapes(startdate, enddate, rperiods, plot_data['y_max'])
    else:
        shapes = []

    if outformat == 'json':
        return plot_data

    # create the high resolution line (ensemble 52)
    scatters.append(go.Scatter(
        name='High Resolution',
        x=plot_data['x_52'],
        y=plot_data[52],
        line=dict(color='black')
    ))
    # create a line for the rest of the ensembles (1-51)
    for i in range(1, 52):
        scatters.append(go.Scatter(
            name='Ensemble ' + str(i),
            x=plot_data['x_1-51'],
            y=plot_data[i],
        ))

    # define a layout for the plot
    layout = go.Layout(
        title=__build_title('Ensemble Predicted Streamflow', reach_id, drain_area),
        xaxis={'title': 'Date'},
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * plot_data['y_max']]
        },
        shapes=shapes
    )
    figure = go.Figure(scatters, layout=layout)
    if outformat == 'plotly':
        return figure
    if outformat == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    return


def records_plot(records: pd.DataFrame, rperiods: pd.DataFrame = None, **kwargs):
    """
    Makes the streamflow saved forecast data and metadata into a plotly plot

    Args:
        records: the csv response from forecast_records
        rperiods: the csv response from return_periods

    Keyword Args
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        reach_id: the reach ID of COMID of a stream to be added to the plot title
        drain_area: a string containing the area and units of the area upstream of this reach that will
        be shown on the plot title

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.record_plot(records, rperiods)
    """
    # Process supported key word arguments (kwargs)
    reach_id = kwargs.get('reach_id', None)
    drain_area = kwargs.get('drain_area', None)
    outformat = kwargs.get('outformat', 'plotly')

    # Validate a few of the important inputs
    if not isinstance(records, pd.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or html')

    # Start processing the inputs
    dates = records.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_values': dates,
        'recorded_flows': records['streamflow (m^3/s)'].dropna(axis=0).tolist(),
        'y_max': max(records['streamflow (m^3/s)']),
    }
    if rperiods is not None:
        plot_data['r2']: rperiods['return_period_2'].values[0]
        plot_data['r5']: rperiods['return_period_5'].values[0]
        plot_data['r10']: rperiods['return_period_10'].values[0]
        plot_data['r25']: rperiods['return_period_25'].values[0]
        plot_data['r50']: rperiods['return_period_50'].values[0]
        plot_data['r100']: rperiods['return_period_100'].values[0]
        shapes = _rperiod_shapes(startdate, enddate, rperiods, plot_data['y_max'])
    else:
        shapes = []

    if outformat == 'json':
        return plot_data

    recorded_flows = go.Scatter(
        name='1st day forecasted flows',
        x=plot_data['x_values'],
        y=plot_data['recorded_flows'],
        line=dict(color='blue'),
    )
    layout = go.Layout(
        title=__build_title('Forecasted Streamflow Record', reach_id, drain_area),
        xaxis={'title': 'Date'},
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * plot_data['y_max']]
        },
        shapes=shapes
    )
    figure = go.Figure([recorded_flows], layout=layout)
    if outformat == 'plotly':
        return figure
    if outformat == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    return


def historical_plot(hist: pd.DataFrame, rperiods: pd.DataFrame = None, **kwargs):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        hist: the csv response from historic_simulation
        rperiods: the csv response from return_periods

    Keyword Args
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        reach_id: the reach ID of COMID of a stream to be added to the plot title
        drain_area: a string containing the area and units of the area upstream of this reach that will
        be shown on the plot title

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.historic_plot(hist, rperiods)
    """
    # Process supported key word arguments (kwargs)
    reach_id = kwargs.get('reach_id', None)
    drain_area = kwargs.get('drain_area', None)
    outformat = kwargs.get('outformat', 'plotly')

    # Validate a few of the important inputs
    if not isinstance(hist, pd.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or plotly or plotly_html')

    dates = hist.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_datetime': dates,
        'y_flow': hist['streamflow (m^3/s)'].tolist(),
        'y_max': max(hist['streamflow (m^3/s)']),
    }
    if rperiods is not None:
        plot_data['r2']: rperiods['return_period_2'].values[0]
        plot_data['r5']: rperiods['return_period_5'].values[0]
        plot_data['r10']: rperiods['return_period_10'].values[0]
        plot_data['r25']: rperiods['return_period_25'].values[0]
        plot_data['r50']: rperiods['return_period_50'].values[0]
        plot_data['r100']: rperiods['return_period_100'].values[0]
        shapes = _rperiod_shapes(startdate, enddate, rperiods, plot_data['y_max'])
    else:
        shapes = []

    if outformat == 'json':
        return plot_data

    layout = go.Layout(
        title=__build_title('Historic Streamflow Simulation', reach_id, drain_area),
        xaxis={
            'title': 'Date',
            'hoverformat': '%b %d %Y',
            'tickformat': '%Y'
        },
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * plot_data['y_max']]
        },
        shapes=shapes
    )
    figure = go.Figure([go.Scatter(x=plot_data['x_datetime'], y=plot_data['y_flow'])], layout=layout)
    if outformat == 'plotly':
        return figure
    if outformat == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    return


def seasonal_plot(seasonal: pd.DataFrame, **kwargs):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        seasonal: the csv response from seasonal_average

    Keyword Argsprobabilities_table
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        reach_id: the reach ID of COMID of a stream to be added to the plot title
        drain_area: a string containing the area and units of the area upstream of this reach that will
        be shown on the plot title

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.seasonal_plot(
                seasonal, reach_id=123456789, drain_area='123 km^2', outformat='json')
    """
    # Process supported key word arguments (kwargs)
    reach_id = kwargs.get('reach_id', None)
    drain_area = kwargs.get('drain_area', None)
    outformat = kwargs.get('outformat', 'plotly')

    # Validate a few of the important inputs
    if not isinstance(seasonal, pd.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or plotly or plotly_html')

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'day_number': seasonal.index.tolist(),
        'average_flow': seasonal['streamflow (m^3/s)'].tolist(),
        'max_flow': seasonal['max_flow'].tolist(),
        'min_flow': seasonal['min_flow'].tolist(),
    }

    if outformat == 'json':
        return plot_data

    avg_flow = go.Scatter(
        name='Average Daily Flow',
        x=plot_data['day_number'],
        y=plot_data['average_flow'],
        line=dict(color='blue')
    )
    max_flow = go.Scatter(
        name='Maximum Daily Flow',
        x=plot_data['day_number'],
        y=plot_data['max_flow'],
        line=dict(color='red')
    )
    min_flow = go.Scatter(
        name='Minimum Daily Flow',
        x=plot_data['day_number'],
        y=plot_data['min_flow'],
        line=dict(color='black')
    )

    layout = go.Layout(
        title=__build_title('Daily Average Streamflow (Historic Simulation)', reach_id, drain_area),
        xaxis={
            'title': 'Date',
            'hoverformat': '%b %d (%j)',
            'tickformat': '%b'
        },
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * max(plot_data['max_flow'])]
        },
    )
    figure = go.Figure([max_flow, avg_flow, min_flow], layout=layout)
    if outformat == 'plotly':
        return figure
    if outformat == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    return


def flow_duration_curve_plot(hist: pd.DataFrame, **kwargs):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        hist: the csv response from historic_simulation

    Keyword Args:
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        reach_id: the reach ID of COMID of a stream to be added to the plot title
        drain_area: a string containing the area and units of the area upstream of this reach that will
            be shown on the plot title

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.flow_duration_curve_plot(hist)
    """
    # Process supported key word arguments (kwargs)
    reach_id = kwargs.get('reach_id', None)
    drain_area = kwargs.get('drain_area', None)
    outformat = kwargs.get('outformat', 'plotly')

    # Validate a few of the important inputs
    if not isinstance(hist, pd.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or plotly or plotly_html')

    # process the hist dataframe to create the flow duration curve
    sorted_hist = hist.sort_values(by='streamflow (m^3/s)', ascending=False)['streamflow (m^3/s)'].tolist()

    # ranks data from smallest to largest
    ranks = len(hist) - scipy.stats.rankdata(sorted_hist, method='average')

    # calculate probability of each rank
    prob = [(ranks[i] / (len(sorted_hist) + 1)) for i in range(len(sorted_hist))]

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_probability': prob,
        'y_flow': sorted_hist,
        'y_max': sorted_hist[0],
    }

    if outformat == 'json':
        return plot_data

    layout = go.Layout(
        title=__build_title('Flow Duration Curve', reach_id, drain_area),
        xaxis={
            'title': 'Date',
            'hoverformat': '%b %d %Y',
            'tickformat': '%Y'
        },
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * plot_data['y_max']]
        },
    )
    figure = go.Figure([go.Scatter(x=plot_data['x_probability'], y=plot_data['y_flow'])], layout=layout)
    if outformat == 'plotly':
        return figure
    if outformat == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    return


def probabilities_table(stats: pd.DataFrame, ensembles: pd.DataFrame, rperiods: pd.DataFrame):
    """
    Processes the results of forecast_stats , forecast_ensembles, and return_periods and uses jinja2 template
    rendering to generate html code that shows the probabilities of exceeding the return period flow on each day.

    Args:
        stats: the csv response from forecast_stats
        ensembles: the csv response from forecast_ensembles
        rperiods: the csv response from return_periods

    Return:
         string containing html to build a table with a row of dates and for exceeding each return period threshold

    Example:
        .. code-block:: python

            data = geoglows.streamflow.probabilities_table(stats, ensembles, rperiods)
    """
    dates = stats.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]
    span = enddate - startdate
    uniqueday = [startdate + datetime.timedelta(days=i) for i in range(span.days + 2)]
    # get the return periods for the stream reach
    rp2 = rperiods['return_period_2'].values
    rp5 = rperiods['return_period_5'].values
    rp10 = rperiods['return_period_10'].values
    rp25 = rperiods['return_period_25'].values
    rp50 = rperiods['return_period_50'].values
    rp100 = rperiods['return_period_100'].values
    # fill the lists of things used as context in rendering the template
    days = []
    r2 = []
    r5 = []
    r10 = []
    r25 = []
    r50 = []
    r100 = []
    for i in range(len(uniqueday) - 1):  # (-1) omit the extra day used for reference only
        tmp = ensembles.loc[uniqueday[i]:uniqueday[i + 1]]
        days.append(uniqueday[i].strftime('%b %d'))
        num2 = 0
        num5 = 0
        num10 = 0
        num25 = 0
        num50 = 0
        num100 = 0
        for column in tmp:
            if any(i > rp100 for i in tmp[column].to_numpy()):
                num2 += 1
                num5 += 1
                num10 += 1
                num25 += 1
                num50 += 1
                num100 += 1
            elif any(i > rp50 for i in tmp[column].to_numpy()):
                num2 += 1
                num5 += 1
                num10 += 1
                num25 += 1
                num50 += 1
            elif any(i > rp25 for i in tmp[column].to_numpy()):
                num2 += 1
                num5 += 1
                num10 += 1
                num25 += 1
            elif any(i > rp10 for i in tmp[column].to_numpy()):
                num2 += 1
                num5 += 1
                num10 += 1
            elif any(i > rp5 for i in tmp[column].to_numpy()):
                num2 += 1
                num5 += 1
            elif any(i > rp2 for i in tmp[column].to_numpy()):
                num2 += 1
        r2.append(round(num2 * 100 / 52))
        r5.append(round(num5 * 100 / 52))
        r10.append(round(num10 * 100 / 52))
        r25.append(round(num25 * 100 / 52))
        r50.append(round(num50 * 100 / 52))
        r100.append(round(num100 * 100 / 52))
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates', 'probabilities_table.html'))
    with open(path) as template:
        return jinja2.Template(template.read()).render(days=days, r2=r2, r5=r5, r10=r10, r25=r25, r50=r50, r100=r100)


def return_periods_table(rperiods: pd.DataFrame) -> str:
    """
    Processes the dataframe response from the return_periods function and uses jinja2 to render an html string for a
    table showing each of the return periods
    Args:
        rperiods: the dataframe from the return periods function

    Returns:
        html string
    """

    # find the correct template to render
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates', 'return_periods_table.html'))
    # work on a copy of the dataframe so you dont ruin the original
    tmp = rperiods
    reach_id = str(tmp.index[0])
    js = json.loads(tmp.to_json())
    rp = {}
    for item in js:
        if item.startswith('return_period'):
            year = item.split('_')[-1]
            rp[f'{year} Year'] = js[item][reach_id]
        elif item == 'max_flow':
            rp['Max Simulated Flow'] = js[item][reach_id]

    rp = {key: round(value, 2) for key, value in sorted(rp.items(), key=lambda item: item[1])}

    with open(path) as template:
        return jinja2.Template(template.read()).render(reach_id=reach_id, rp=rp, colors=_plot_colors())


# PLOTTING AUXILIARY FUNCTIONS
def __build_title(base, reach_id, drain_area):
    if reach_id:
        base += '<br>Stream ID: ' + str(reach_id)
    if drain_area:
        base += '<br>Upstream Drainage Area: ' + str(drain_area)
    return base


def _plot_colors():
    return {
        '2 Year': 'rgba(254, 240, 1, .4)',
        '5 Year': 'rgba(253, 154, 1, .4)',
        '10 Year': 'rgba(255, 56, 5, .4)',
        '20 Year': 'rgba(128, 0, 246, .4)',
        '25 Year': 'rgba(255, 0, 0, .4)',
        '50 Year': 'rgba(128, 0, 106, .4)',
        '100 Year': 'rgba(128, 0, 246, .4)',
    }


def _rperiod_shapes(startdate: str, enddate: str, rperiods: pd.DataFrame, y_max: float):
    colors = _plot_colors()
    linestyle = {'width': .3}
    if list(rperiods.columns) == ['max_flow', 'return_period_20', 'return_period_10', 'return_period_2']:
        return [
            go.layout.Shape(
                type='rect',
                x0=startdate,
                x1=enddate,
                y0=rperiods['return_period_2'].values[0],
                y1=rperiods['return_period_10'].values[0],
                line=linestyle,
                fillcolor=colors['2 Year']
            ),
            go.layout.Shape(
                type='rect',
                x0=startdate,
                x1=enddate,
                y0=rperiods['return_period_10'].values[0],
                y1=rperiods['return_period_20'].values[0],
                line=linestyle,
                fillcolor=colors['10 Year']
            ),
            go.layout.Shape(
                type='rect',
                x0=startdate,
                x1=enddate,
                y0=rperiods['return_period_10'].values[0],
                y1=1.2 * y_max,
                line=linestyle,
                fillcolor=colors['20 Year']
            ),
        ]
    return [
        go.layout.Shape(
            type='rect',
            x0=startdate,
            x1=enddate,
            y0=rperiods['return_period_2'].values[0],
            y1=rperiods['return_period_5'].values[0],
            line=linestyle,
            fillcolor=colors['2 Year']
        ),
        go.layout.Shape(
            type='rect',
            x0=startdate,
            x1=enddate,
            y0=rperiods['return_period_5'].values[0],
            y1=rperiods['return_period_10'].values[0],
            line=linestyle,
            fillcolor=colors['5 Year']
        ),
        go.layout.Shape(
            type='rect',
            x0=startdate,
            x1=enddate,
            y0=rperiods['return_period_10'].values[0],
            y1=rperiods['return_period_25'].values[0],
            line=linestyle,
            fillcolor=colors['10 Year']
        ),
        go.layout.Shape(
            type='rect',
            x0=startdate,
            x1=enddate,
            y0=rperiods['return_period_25'].values[0],
            y1=rperiods['return_period_50'].values[0],
            line=linestyle,
            fillcolor=colors['25 Year']
        ),
        go.layout.Shape(
            type='rect',
            x0=startdate,
            x1=enddate,
            y0=rperiods['return_period_50'].values[0],
            y1=rperiods['return_period_100'].values[0],
            line=linestyle,
            fillcolor=colors['50 Year']
        ),
        go.layout.Shape(
            type='rect',
            x0=startdate,
            x1=enddate,
            y0=rperiods['return_period_100'].values[0],
            y1=1.2 * y_max,
            line=linestyle,
            fillcolor=colors['100 Year']
        ),
    ]


# API AUXILIARY FUNCTION
def _make_request(endpoint: str, method: str, params: dict, return_format: str):
    if return_format == 'request':
        params['return_format'] == 'csv'

    # request the data from the API
    data = requests.get(endpoint + method, params=params)

    # process the response from the API as appropriate to make the corresponding python object
    if return_format == 'csv':
        if method == 'ForecastWarnings/':
            return pandas.read_csv(StringIO(data.text), index_col='comid')
        if method == 'ReturnPeriods/':
            return pandas.read_csv(StringIO(data.text), index_col='rivid')
        if method == 'SeasonalAverage/':
            tmp = pandas.read_csv(StringIO(data.text), index_col='day_of_year')
            tmp.index = pandas.to_datetime(tmp.index + 1, format='%j').strftime('%b %d')
            return tmp
        tmp = pandas.read_csv(StringIO(data.text), index_col='datetime')
        tmp.index = pandas.to_datetime(tmp.index)
        return tmp
    elif return_format == 'json':
        return json.loads(data.text)
    elif return_format == 'waterml':
        return data.text
    elif return_format == 'request':
        return data
    else:
        raise ValueError('Unsupported return format requested: ' + str(return_format))
