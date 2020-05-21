import datetime
import json
import os
from collections import OrderedDict
from io import StringIO

import jinja2
import pandas
import pandas as pd
import plotly.graph_objs as go
import requests
import scipy.stats
from plotly.offline import plot as offline_plot
from shapely.geometry import Point, MultiPoint, box
from shapely.ops import nearest_points

__all__ = ['forecast_stats', 'forecast_ensembles', 'forecast_warnings', 'forecast_records', 'historic_simulation',
           'seasonal_average', 'return_periods', 'available_data', 'available_dates', 'available_regions',
           'hydroviewer_plot', 'forecast_plot', 'records_plot', 'ensembles_plot', 'historical_plot', 'seasonal_plot',
           'flow_duration_curve_plot', 'probabilities_table', 'return_periods_table', 'reach_to_region',
           'latlon_to_reach']

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


def latlon_to_reach(lat: float, lon: float) -> dict:
    """
    Uses a list of lat/lon for each reach_id to find the closest stream reach to a given lat/lon location

    Args:
        lat: a valid latitude
        lon: a valid longitude

    Return:
        a dictionary containing the reach_id as well as the name of the region and the distance
        from the provided lat and lon to the stream in units of degrees.

    Example:
        .. code-block:: python

            stream_data = latlon_to_reach(10, 50)
            {'reach_id': 123456, 'region': 'example_region-geoglows', 'distance': .05}
    """
    if lat is False or lon is False:
        raise ValueError('provide a valid latitude and longitude to in order to find a reach_id')

    # determine the region that the point is in
    region = latlon_to_region(lat, lon)

    # switch the point because the csv's are lat/lon, backwards from what shapely expects (lon then lat)
    point = Point(float(lat), float(lon))

    # open the region csv
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'delineation_data'))
    df = pandas.read_csv(os.path.join(base_path, region, 'comid_lat_lon_z.csv'), sep=',', header=0, index_col=0)
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

    Example:
        .. code-block:: python

            stream_data = latlon_to_region(10, 50)
    """
    if lat is False or lon is False:
        raise ValueError('provide a valid latitude and longitude to in order to find a region')

    # open the bounding boxes csv, figure out which regions the point lies within
    point = Point(float(lon), float(lat))
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'delineation_data'))
    bb_csv = pandas.read_csv(os.path.join(base_path, 'bounding_boxes.csv'), index_col='region')
    for row in bb_csv.iterrows():
        bbox = box(row[1][0], row[1][1], row[1][2], row[1][3])
        if point.within(bbox):
            return row[0]
    # if there weren't any regions, return that there was an error
    raise ValueError('This point is not within any of the supported delineation regions.')


# FUNCTIONS THAT PROCESS THE RESULTS OF THE API INTO A PLOTLY PLOT OR DICTIONARY
def hydroviewer_plot(records: pd.DataFrame,
                     stats: pd.DataFrame,
                     ensembles: pd.DataFrame,
                     rperiods: pd.DataFrame = None,
                     record_days: int = 7,
                     outformat: str = 'plotly', **kwargs):
    """
    Creates the standard plot for a hydroviewer

    Args:
        records: the response from forecast_records
        stats: the response from forecast_stats
        ensembles: the csv response from forecast_ensembles
        rperiods: (optional) the response from return_periods
        outformat: (optional) either 'json', 'plotly', or 'plotly_html' (default plotly)
        record_days: (optional) number of days of forecast records to show before the start of the forecast

    Keyword Args:
        reach_id: the reach ID of COMID of a stream to be added to the plot title
        drain_area: a string containing the area and units of the area upstream of this reach that will be shown on the
            plot title

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.hydroviewer_plot(records, stats, rperiods)
    """
    # Process supported key word arguments (kwargs)
    reach_id = kwargs.get('reach_id', None)
    drain_area = kwargs.get('drain_area', None)

    # Validate a few of the important inputs
    if not isinstance(records, pd.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, or plotly_html')

    # determine the bounds of the plot on the x and y axis
    stats_dates = stats.index.tolist()
    # limit the forecast records to 7 days before the start of the forecast
    records = records[records.index >= pd.to_datetime(stats_dates[0] - datetime.timedelta(days=record_days))]
    records_dates = records.index.tolist()
    if len(records_dates) == 0:
        startdate = stats_dates[0]
        enddate = stats_dates[-1]
    else:
        startdate = min(records_dates[0], stats_dates[0])
        enddate = max(records_dates[-1], stats_dates[-1])
    max_flow = max(records['streamflow_m^3/s'].max(), stats['flow_max_m^3/s'].max())

    # build a json of data for this plot by combining the other individual plot functions
    if outformat == 'json':
        plot_data = forecast_plot(stats, rperiods, outformat='json')
        plot_data.update(ensembles_plot(ensembles, outformat='json'))
        plot_data.update(records_plot(records, outformat='json'))
        plot_data['y_max'] = max_flow
        return plot_data

    # start building the plotly graph object
    figure = records_plot(records, outformat='plotly')
    for new_scatter in forecast_plot(stats, outformat='plotly_scatters'):
        figure.add_trace(new_scatter)

    # do the ensembles separately so we can group then and make only 1 legend entry
    ensemble_data = ensembles_plot(ensembles, outformat='json')
    figure.add_trace(go.Scatter(
        x=ensemble_data['x_1-51'],
        y=ensemble_data['ensemble_01_m^3/s'],
        visible='legendonly',
        legendgroup='ensembles',
        name='Forecast Ensembles',
    ))
    for i in range(2, 52):
        figure.add_trace(go.Scatter(
            x=ensemble_data['x_1-51'],
            y=ensemble_data[f'ensemble_{i:02}_m^3/s'],
            visible='legendonly',
            legendgroup='ensembles',
            name=f'Ensemble {i}',
            showlegend=False,
        ))
    if rperiods is not None:
        max_visible = max(stats['flow_75%_m^3/s'].max(), stats['flow_avg_m^3/s'].max(), stats['high_res_m^3/s'].max(),
                          records['streamflow_m^3/s'].max())
        for rp in _rperiod_scatters(startdate, enddate, rperiods, max_flow, max_visible):
            figure.add_trace(rp)

    figure.update_layout(
        title=__build_title('Forecasted Streamflow', reach_id, drain_area),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'range': [startdate, enddate]},
    )

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
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    # Start processing the inputs
    dates = stats.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_stats': stats['flow_avg_m^3/s'].dropna(axis=0).index.tolist(),
        'x_hires': stats['high_res_m^3/s'].dropna(axis=0).index.tolist(),
        'y_max': max(stats['flow_max_m^3/s']),
        'flow_max': list(stats['flow_max_m^3/s'].dropna(axis=0)),
        'flow_75%': list(stats['flow_75%_m^3/s'].dropna(axis=0)),
        'flow_avg': list(stats['flow_avg_m^3/s'].dropna(axis=0)),
        'flow_25%': list(stats['flow_25%_m^3/s'].dropna(axis=0)),
        'flow_min': list(stats['flow_min_m^3/s'].dropna(axis=0)),
        'high_res': list(stats['high_res_m^3/s'].dropna(axis=0)),
    }
    if rperiods is not None:
        plot_data.update(rperiods.to_dict(orient='index').items())
        max_visible = max(max(plot_data['flow_75%']), max(plot_data['flow_avg']), max(plot_data['high_res']))
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rperiods, plot_data['y_max'], max_visible)
    else:
        rperiod_scatters = []
    if outformat == 'json':
        return plot_data

    scatter_plots = [
                        # Plot together so you can use fill='toself' for the shaded box, also separately so the labels appear
                        go.Scatter(name='Maximum & Minimum',
                                   x=plot_data['x_stats'] + plot_data['x_stats'][::-1],
                                   y=plot_data['flow_max'] + plot_data['flow_min'][::-1],
                                   legendgroup='boundaries',
                                   fill='toself',
                                   visible='legendonly',
                                   line=dict(color='lightblue', dash='dash')),
                        go.Scatter(name='Maximum',
                                   x=plot_data['x_stats'],
                                   y=plot_data['flow_max'],
                                   legendgroup='boundaries',
                                   visible='legendonly',
                                   showlegend=False,
                                   line=dict(color='darkblue', dash='dash')),
                        go.Scatter(name='Minimum',
                                   x=plot_data['x_stats'],
                                   y=plot_data['flow_min'],
                                   legendgroup='boundaries',
                                   visible='legendonly',
                                   showlegend=False,
                                   line=dict(color='darkblue', dash='dash')),

                        go.Scatter(name='25-75 Percentile Flow',
                                   x=plot_data['x_stats'] + plot_data['x_stats'][::-1],
                                   y=plot_data['flow_75%'] + plot_data['flow_25%'][::-1],
                                   legendgroup='percentile_flow',
                                   fill='toself',
                                   line=dict(color='lightgreen'), ),
                        go.Scatter(name='75%',
                                   x=plot_data['x_stats'],
                                   y=plot_data['flow_75%'],
                                   showlegend=False,
                                   legendgroup='percentile_flow',
                                   line=dict(color='green'), ),
                        go.Scatter(name='25%',
                                   x=plot_data['x_stats'],
                                   y=plot_data['flow_25%'],
                                   showlegend=False,
                                   legendgroup='percentile_flow',
                                   line=dict(color='green'), ),

                        go.Scatter(name='Higher Resolution',
                                   x=plot_data['x_hires'],
                                   y=plot_data['high_res'],
                                   line={'color': 'black'}, ),
                        go.Scatter(name='Average',
                                   x=plot_data['x_stats'],
                                   y=plot_data['flow_avg'],
                                   line=dict(color='blue'), ),
                    ] + rperiod_scatters

    if outformat == 'plotly_scatters':
        return scatter_plots

    layout = go.Layout(
        title=__build_title('Forecasted Streamflow', reach_id, drain_area),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y', 'tickformat': '%b %d %Y'},
        legend_title_text='Streamflow Series',
    )
    figure = go.Figure(scatter_plots, layout=layout)
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
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    # variables to determine the maximum flow and hold all the scatter plot lines
    max_flows = []
    scatter_plots = []

    # determine the threshold values for return periods and the start/end dates so we can plot them
    dates = ensembles.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    # process the series' components and store them in a dictionary
    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_1-51': ensembles['ensemble_01_m^3/s'].dropna(axis=0).index.tolist(),
        'x_52': ensembles['ensemble_52_m^3/s'].dropna(axis=0).index.tolist(),
    }

    # add a dictionary entry for each of the ensemble members. the key for each series is the integer ensemble number
    for ensemble in ensembles.columns:
        plot_data[ensemble] = ensembles[ensemble].dropna(axis=0).tolist()
        max_flows.append(max(plot_data[ensemble]))
    plot_data['y_max'] = max(max_flows)

    if rperiods is not None:
        plot_data.update(rperiods.to_dict(orient='index').items())
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rperiods, plot_data['y_max'])
    else:
        rperiod_scatters = []
    if outformat == 'json':
        return plot_data

    # create the high resolution line (ensemble 52)
    scatter_plots.append(go.Scatter(
        name='High Resolution',
        x=plot_data['x_52'],
        y=plot_data['ensemble_52_m^3/s'],
        line=dict(color='black')
    ))
    # create a line for the rest of the ensembles (1-51)
    for i in range(1, 52):
        scatter_plots.append(go.Scatter(
            name='Ensemble ' + str(i),
            x=plot_data['x_1-51'],
            y=plot_data[f'ensemble_{i:02}_m^3/s'],
        ))
    scatter_plots += rperiod_scatters

    if outformat == 'plotly_scatters':
        return scatter_plots

    # define a layout for the plot
    layout = go.Layout(
        title=__build_title('Ensemble Predicted Streamflow', reach_id, drain_area),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 1.2 * plot_data['y_max']]},
        xaxis={'title': 'Date', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y', 'tickformat': '%b %d %Y'},
        legend_title_text='Streamflow Series',
    )
    figure = go.Figure(scatter_plots, layout=layout)
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
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    # Start processing the inputs
    dates = records.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_records': dates,
        'recorded_flows': records['streamflow_m^3/s'].dropna(axis=0).tolist(),
        'y_max': max(records['streamflow_m^3/s']),
    }
    if rperiods is not None:
        plot_data.update(rperiods.to_dict(orient='index').items())
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rperiods, plot_data['y_max'], plot_data['y_max'])
    else:
        rperiod_scatters = []
    if outformat == 'json':
        return plot_data

    scatter_plots = [go.Scatter(
        name='1st day forecasts',
        x=plot_data['x_records'],
        y=plot_data['recorded_flows'],
        line=dict(color='gold'),
    )] + rperiod_scatters

    if outformat == 'plotly_scatters':
        return scatter_plots

    layout = go.Layout(
        title=__build_title('Forecasted Streamflow Record', reach_id, drain_area),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 1.2 * plot_data['y_max']]},
        xaxis={'title': 'Date', 'range': [startdate, enddate]},
        legend_title_text='Streamflow Series',
    )
    figure = go.Figure(scatter_plots, layout=layout)
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
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    dates = hist.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_datetime': dates,
        'y_flow': hist['streamflow_m^3/s'].tolist(),
        'y_max': max(hist['streamflow_m^3/s']),
    }
    if rperiods is not None:
        plot_data.update(rperiods.to_dict(orient='index').items())
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rperiods, plot_data['y_max'], plot_data['y_max'])
    else:
        rperiod_scatters = []

    if outformat == 'json':
        return plot_data

    scatter_plots = [
                        go.Scatter(
                            name='Historic Simulation',
                            x=plot_data['x_datetime'],
                            y=plot_data['y_flow'])
                    ] + rperiod_scatters

    if outformat == 'plotly_scatters':
        return scatter_plots

    layout = go.Layout(
        title=__build_title('Historic Streamflow Simulation', reach_id, drain_area),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y', 'tickformat': '%Y'},
        legend_title_text='Streamflow Series',
    )
    figure = go.Figure(scatter_plots, layout=layout)
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
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'day_number': seasonal.index.tolist(),
        'average_flow': seasonal['streamflow_m^3/s'].tolist(),
        'max_flow': seasonal['max_flow'].tolist(),
        'min_flow': seasonal['min_flow'].tolist(),
    }
    if outformat == 'json':
        return plot_data

    scatter_plots = [
        go.Scatter(
            name='Average Daily Flow',
            x=plot_data['day_number'],
            y=plot_data['average_flow'],
            line=dict(color='blue')
        ),
        go.Scatter(
            name='Maximum Daily Flow',
            x=plot_data['day_number'],
            y=plot_data['max_flow'],
            line=dict(color='red')
        ),
        go.Scatter(
            name='Minimum Daily Flow',
            x=plot_data['day_number'],
            y=plot_data['min_flow'],
            line=dict(color='black')
        ),
    ]
    if outformat == 'plotly_scatters':
        return scatter_plots
    layout = go.Layout(
        title=__build_title('Daily Average Streamflow (Historic Simulation)', reach_id, drain_area),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'range': [plot_data['day_number'][0], plot_data['day_number'][1]],
               'hoverformat': '%b %d (%j)', 'tickformat': '%b'},
        legend_title_text='Streamflow Series',
    )
    figure = go.Figure(scatter_plots, layout=layout)
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
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    # process the hist dataframe to create the flow duration curve
    sorted_hist = hist.sort_values(by='streamflow_m^3/s', ascending=False)['streamflow_m^3/s'].tolist()

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

    scatter_plots = [
        go.Scatter(
            name='Flow Duration Curve',
            x=plot_data['x_probability'],
            y=plot_data['y_flow'])
    ]
    if outformat == 'plotly_scatters':
        return scatter_plots
    layout = go.Layout(
        title=__build_title('Flow Duration Curve', reach_id, drain_area),
        xaxis={'title': 'Exceedence Probability'},
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        legend_title_text='Streamflow Series',
    )
    figure = go.Figure(scatter_plots, layout=layout)
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
        return jinja2.Template(template.read()).render(days=days, r2=r2, r5=r5, r10=r10, r25=r25, r50=r50, r100=r100,
                                                       colors=_plot_colors())


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


def _rperiod_scatters(startdate: str, enddate: str, rperiods: pd.DataFrame, y_max: float, max_visible: float = 0):
    colors = _plot_colors()
    x_vals = (startdate, enddate, enddate, startdate)
    r2 = int(rperiods['return_period_2'].values[0])
    if max_visible > r2:
        visible = True
    else:
        visible = 'legendonly'

    def template(name, y, color):
        return go.Scatter(
            name=name,
            x=x_vals,
            y=y,
            legendgroup='returnperiods',
            fill='toself',
            visible=visible,
            line=dict(color=color, width=0))

    if list(rperiods.columns) == ['max_flow', 'return_period_20', 'return_period_10', 'return_period_2']:
        r10 = int(rperiods['return_period_10'].values[0])
        r20 = int(rperiods['return_period_20'].values[0])
        rmax = int(max(2 * r20 - r10, y_max))
        return [
            template(f'2 Year: {r2}', (r2, r2, r10, r10), colors['2 Year']),
            template(f'10 Year: {r10}', (r10, r10, r20, r20), colors['10 Year']),
            template(f'20 Year: {r20}', (r20, r20, rmax, rmax), colors['20 Year']),
        ]

    else:
        r5 = int(rperiods['return_period_5'].values[0])
        r10 = int(rperiods['return_period_10'].values[0])
        r25 = int(rperiods['return_period_25'].values[0])
        r50 = int(rperiods['return_period_50'].values[0])
        r100 = int(rperiods['return_period_100'].values[0])
        rmax = int(max(2 * r100 - r25, y_max))
        return [
        go.Scatter(name='Return Periods',
                   x=(startdate, enddate, enddate, startdate),
                   y=(r2, r2, rmax, rmax),
                   legendgroup='returnperiods',
                   visible=visible,
                   line=dict(color='rgba(0,0,0,0)', width=0)),
        template(f'2 Year: {r2}', (r2, r2, r5, r5), colors['2 Year']),
        template(f'5 Year: {r5}', (r5, r5, r10, r10), colors['5 Year']),
        template(f'10 Year: {r10}', (r10, r10, r25, r25), colors['10 Year']),
        template(f'25 Year: {r25}', (r25, r25, r50, r50), colors['25 Year']),
        template(f'50 Year: {r50}', (r50, r50, r100, r100), colors['50 Year']),
        template(f'100 Year: {r100}', (r100, r100, rmax, rmax), colors['100 Year']),
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
