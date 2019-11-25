import pandas
import requests
import json
import datetime
import jinja2
import os
import math
import scipy.stats
from plotly.offline import plot as offline_plot
from plotly.graph_objs import Scatter, Layout, Figure
import plotly.graph_objs as go
from io import StringIO
from collections import OrderedDict, namedtuple
from shapely.geometry import Point, MultiPoint, box
from shapely.ops import nearest_points

BYU_ENDPOINT = 'https://tethys2.byu.edu/localsptapi/api/'


# FUNCTIONS THAT CALL THE GLOBAL STREAMFLOW PREDICTION API
def forecast_stats(reach_id=None, lat=None, lon=None, endpoint=BYU_ENDPOINT, token=None, return_format='csv'):
    """
    Retrieves statistics that summarize the most recent streamflow forecast. You need to specify either a reach_id or
    both a lat and lon.

    Args:
        reach_id (int): the ID of a stream
        lat (int): a valid latitude
        lon (int): a valid longitude
        endpoint (str): the endpoint of an api instance
        token (dict): dictionary with the header for api key validation (if applicable to the endpoint)
        return_format (str): 'csv', 'json', 'waterml', 'request'

    Return:
        return_format='csv' returns a pandas dataframe
        return_format='json' returns a json
        return_format='waterml' returns a waterml string
        return_format='request' returns a request response object

    Return Format:
        pandas.DataFrame

    Example:
        .. code-block:: python

            # using a reach_id
            data = geoglows.streamflow.forecast_ensembles(12341234)
            # using lat and lon as keyword arguments instead of reach_id
            data = geoglows.streamflow.forecast_ensembles(lat=10, lon=10)
    """
    # validate arguments
    params = __validate_api_params(reach_id, lat, lon, return_format)
    data = requests.get(endpoint + 'ForecastStats/', headers=token, params=params)

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data.text))
    elif return_format == 'json':
        return json.loads(data.text)
    elif return_format == 'waterml':
        return data.text
    elif return_format == 'request':
        return data


def forecast_ensembles(reach_id=None, lat=None, lon=None, endpoint=BYU_ENDPOINT, token=None, return_format='csv'):
    """
    Retrieves each ensemble from the most recent streamflow forecast. You need to specify either a reach_id or
    both a lat and lon.

    Args:
        reach_id (int): the ID of a stream
        lat (int): a valid latitude
        lon (int): a valid longitude
        endpoint (str): the endpoint of an api instance
        token (dict): dictionary with the header for api key validation (if applicable to the endpoint)
        return_format (str): 'csv', 'json', 'waterml', 'request'

    Return:
        return_format='csv' returns a pandas dataframe
        return_format='json' returns a json
        return_format='waterml' returns a waterml string
        return_format='request' returns a request response object

    Example:
        .. code-block:: python

            data = geoglows.streamflow.forecast_ensembles(12341234)
    """
    # validate arguments
    params = __validate_api_params(reach_id, lat, lon, return_format)
    data = requests.get(endpoint + 'ForecastEnsembles/', headers=token, params=params)

    if return_format == 'csv':
        tmp = pandas.read_csv(StringIO(data.text), index_col='datetime')
        tmp.index = pandas.to_datetime(tmp.index)
        return tmp
    elif return_format == 'json':
        return json.loads(data.text)
    elif return_format == 'waterml':
        return data.text
    elif return_format == 'request':
        return data


def historic_simulation(reach_id=None, lat=None, lon=None, endpoint=BYU_ENDPOINT, token=None, return_format='csv'):
    """
    Retrieves historical streamflow simulation derived from the ERA-Interim dataset. You need to specify either a
    reach_id or both a lat and lon.

    Args:
        reach_id (int): the ID of a stream
        lat (int): a valid latitude
        lon (int): a valid longitude
        endpoint (str): the endpoint of an api instance
        token (dict): dictionary with the header for api key validation (if applicable to the endpoint)
        return_format (str): 'csv', 'json', 'waterml', 'request'

    Return:
        return_format='csv' returns a pandas dataframe
        return_format='json' returns a json
        return_format='waterml' returns a waterml string
        return_format='request' returns a request response object

    Example:
        .. code-block:: python

            data = geoglows.streamflow.historic_simulation(12341234)
    """
    # validate arguments
    params = __validate_api_params(reach_id, lat, lon, return_format)
    data = requests.get(endpoint + 'HistoricSimulation/', headers=token, params=params)

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data.text))
    elif return_format == 'json':
        return json.loads(data.text)
    elif return_format == 'waterml':
        return data.text
    elif return_format == 'request':
        return data


def seasonal_average(reach_id=None, lat=None, lon=None, endpoint=BYU_ENDPOINT, token=None, return_format='csv'):
    """
    Retrieves the average flow for every day of the year. You need to specify either a reach_id or both a lat and lon.

    Args:
        reach_id (int): the ID of a stream
        lat (int): a valid latitude
        lon (int): a valid longitude
        endpoint (str): the endpoint of an api instance
        token (dict): dictionary with the header for api key validation (if applicable to the endpoint)
        return_format (str): 'csv', 'json', 'waterml', 'request'

    Return:
        return_format='csv' returns a pandas dataframe
        return_format='json' returns a json
        return_format='waterml' returns a waterml string
        return_format='request' returns a request response object

    Example:
        .. code-block:: python

            data = geoglows.streamflow.seasonal_average(12341234)
    """
    # validate arguments
    params = __validate_api_params(reach_id, lat, lon, return_format)
    data = requests.get(endpoint + 'SeasonalAverage/', headers=token, params=params)

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data.text))
    elif return_format == 'json':
        return json.loads(data.text)
    elif return_format == 'waterml':
        return data.text
    elif return_format == 'request':
        return data


def return_periods(reach_id=None, lat=None, lon=None, endpoint=BYU_ENDPOINT, token=None, return_format='csv'):
    """
    Retrieves the return period thresholds for 2, 10, 20 year flow events. You need to specify either a reach_id or
    both a lat and lon.

    Args:
        reach_id (int): the ID of a stream
        lat (int): a valid latitude
        lon (int): a valid longitude
        endpoint (str): the endpoint of an api instance
        token (dict): dictionary with the header for api key validation (if applicable to the endpoint)
        return_format (str): 'csv', 'json', 'waterml', 'request'

    Return:
        return_format='csv' returns a pandas dataframe
        return_format='json' returns a json
        return_format='waterml' returns a waterml string
        return_format='request' returns a request response object

    Example:
        .. code-block:: python

            data = geoglows.streamflow.return_periods(12341234)
    """
    # validate arguments
    params = __validate_api_params(reach_id, lat, lon, return_format)
    data = requests.get(endpoint + 'ReturnPeriods/', headers=token, params=params)

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data.text), index_col='return period')
    elif return_format == 'json':
        return json.loads(data.text)
    elif return_format == 'waterml':
        return data.text
    elif return_format == 'request':
        return data


def available_dates(reach_id=None, region=None, endpoint=BYU_ENDPOINT, token=None):
    """
    Retrieves the list of dates of stored streamflow forecasts. You need to specify either a reach_id or a region.

    Args:
        reach_id (int): the ID of a stream
        region (str): the name of a hydrologic region used in the model
        endpoint (str): the endpoint of an api instance
        token (dicti): dictionary with the header for api key validation (if applicable to the endpoint)

    Return:
        dates (json): {'available_dates': ['list_of_dates']}

    Example:
        .. code-block:: python

            data = geoglows.streamflow.available_dates(12341234)
    """
    # you need a region for the api call, so the user needs to provide one or a valid reach_id to get it from
    if region:
        params = {'region': region}
    elif reach_id:
        params = {'region': reach_to_region(reach_id)}
    else:
        raise RuntimeError('specify a region or a reach_id')

    return json.loads(requests.get(endpoint + 'AvailableDates/', headers=token, params=params).text)


def available_regions(endpoint=BYU_ENDPOINT, token=None):
    """
    Retrieves a list of regions available at the endpoint

    Args:
        endpoint (str): the endpoint of an api instance
        token (dict): dictionary with the header for api key validation (if applicable to the endpoint)

    Return:
        dates (json): {'available_regions': ['list_of_regions']}

    Example:
        .. code-block:: python

            data = geoglows.streamflow.available_regions(12341234)
    """
    return json.loads(requests.get(endpoint + 'AvailableRegions/', headers=token).text)


# FUNCTIONS THAT PROCESS THE RESULTS OF THE API INTO A PLOTLY PLOT OR DICTIONARY
def forecast_plot(stats, rperiods, **kwargs):
    """
    Makes the streamflow data and optional metadata into a plotly plot

    Args:
        stats (pandas.DataFrame): the csv response from `forecast_stats`_
        rperiods (pandas.DataFrame): the csv response from `return_periods`_

    :keyword string outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
    :keyword int reach_id: the reach ID of COMID of a stream to be added to the plot title
    :keyword string drain_area: a string containing the area and units of the area upstream of this reach that will
        be shown on the plot title

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
    if not isinstance(stats, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or html')

    # Start processing the inputs
    dates = stats['datetime'].tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_ensembles': stats[['datetime', 'mean (m3/s)']].dropna(axis=0)['datetime'].tolist(),
        'x_hires': stats[['datetime', 'high_res (m3/s)']].dropna(axis=0)['datetime'].tolist(),
        'y_max': max(stats['max (m3/s)']),
        'min': list(stats['min (m3/s)'].dropna(axis=0)),
        'mean': list(stats['mean (m3/s)'].dropna(axis=0)),
        'max': list(stats['max (m3/s)'].dropna(axis=0)),
        'stdlow': list(stats['std_dev_range_lower (m3/s)'].dropna(axis=0)),
        'stdup': list(stats['std_dev_range_upper (m3/s)'].dropna(axis=0)),
        'hires': list(stats['high_res (m3/s)'].dropna(axis=0)),
        'r2': rperiods.iloc[3][0],
        'r10': rperiods.iloc[2][0],
        'r20': rperiods.iloc[1][0],
    }

    if outformat == 'json':
        return plot_data

    meanplot = Scatter(
        name='Mean',
        x=plot_data['x_ensembles'],
        y=plot_data['mean'],
        line=dict(color='blue'),
    )
    maxplot = Scatter(
        name='Max',
        x=plot_data['x_ensembles'],
        y=plot_data['max'],
        fill='tonexty',
        mode='lines',
        line=dict(color='rgb(152, 251, 152)', width=0)
    )
    minplot = Scatter(
        name='Min',
        x=plot_data['x_ensembles'],
        y=plot_data['min'],
        fill=None,
        mode='lines',
        line=dict(color='rgb(152, 251, 152)')
    )
    stdlowplot = Scatter(
        name='Std. Dev. Lower',
        x=plot_data['x_ensembles'],
        y=plot_data['stdlow'],
        fill='tonexty',
        mode='lines',
        line=dict(color='rgb(152, 251, 152)', width=0)
    )
    stdupplot = Scatter(
        name='Std. Dev. Upper',
        x=plot_data['x_ensembles'],
        y=plot_data['stdup'],
        fill='tonexty',
        mode='lines',
        line={'width': 0, 'color': 'rgb(34, 139, 34)'}
    )
    hires = Scatter(
        name='Higher Resolution',
        x=plot_data['x_hires'],
        y=plot_data['hires'],
        line={'color': 'black'}
    )
    layout = Layout(
        title=__build_title('Forecasted Streamflow', reach_id, drain_area),
        xaxis={'title': 'Date'},
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * plot_data['y_max']]
        },
        shapes=__rperiod_shapes(
            startdate, enddate, plot_data['r2'], plot_data['r10'], plot_data['r20'], plot_data['y_max'])
    )
    figure = Figure([minplot, stdlowplot, stdupplot, maxplot, meanplot, hires], layout=layout)
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


def ensembles_plot(ensembles, rperiods, **kwargs):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        ensembles (pandas.DataFrame): the csv response from `forecast_ensembles`_
        rperiods (pandas.DataFrame): the csv response from `return_periods`_

    :keyword string outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
    :keyword int reach_id: the reach ID of COMID of a stream to be added to the plot title
    :keyword string drain_area: a string containing the area and units of the area upstream of this reach that will
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
    if not isinstance(ensembles, pandas.DataFrame):
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
        'x_1-51': ensembles['ensemble_01 (m3/s)'].dropna(axis=0).index.tolist(),
        'x_52': ensembles['ensemble_52 (m3/s)'].dropna(axis=0).index.tolist(),
        'r2': rperiods.iloc[3][0],
        'r10': rperiods.iloc[2][0],
        'r20': rperiods.iloc[1][0],
    }

    # add a dictionary entry for each of the ensemble members. the key for each series is the integer ensemble number
    for ensemble in ensembles.columns:
        plot_data[int(ensemble[9:11])] = ensembles[ensemble].dropna(axis=0).tolist()
        max_flows.append(max(plot_data[int(ensemble[9:11])]))
    plot_data['y_max'] = max(max_flows)

    if outformat == 'json':
        return plot_data

    # create the high resolution line (ensemble 52)
    scatters.append(Scatter(
        name='High Resolution',
        x=plot_data['x_52'],
        y=plot_data[52],
        line=dict(color='black')
    ))
    # create a line for the rest of the ensembles (1-51)
    for i in range(1, 52):
        scatters.append(Scatter(
            name='Ensemble ' + str(i),
            x=plot_data['x_1-51'],
            y=plot_data[i],
        ))

    # define a layout for the plot
    layout = Layout(
        title=__build_title('Ensemble Predicted Streamflow', reach_id, drain_area),
        xaxis={'title': 'Date'},
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * plot_data['y_max']]
        },
        shapes=__rperiod_shapes(
            startdate, enddate, plot_data['r2'], plot_data['r10'], plot_data['r20'], plot_data['y_max'])
    )
    figure = Figure(scatters, layout=layout)
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


def historical_plot(hist, rperiods, **kwargs):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        hist (pandas.DataFrame): the csv response from `historic_simulation`_
        rperiods (pandas.DataFrame): the csv response from `return_periods`_

    :keyword string outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
    :keyword int reach_id: the reach ID of COMID of a stream to be added to the plot title
    :keyword string drain_area: a string containing the area and units of the area upstream of this reach that will
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
    if not isinstance(hist, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or plotly or plotly_html')

    dates = hist['datetime'].tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_datetime': dates,
        'y_flow': hist['streamflow (m3/s)'].tolist(),
        'y_max': max(hist['streamflow (m3/s)']),
        'r2': rperiods.iloc[3][0],
        'r10': rperiods.iloc[2][0],
        'r20': rperiods.iloc[1][0],
    }

    if outformat == 'json':
        return plot_data

    layout = Layout(
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
        shapes=__rperiod_shapes(
            startdate, enddate, plot_data['r2'], plot_data['r10'], plot_data['r20'], plot_data['y_max'])
    )
    figure = Figure([Scatter(x=plot_data['x_datetime'], y=plot_data['y_flow'])], layout=layout)
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


def seasonal_plot(seasonal, **kwargs):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        seasonal (pandas.DataFrame): the csv response from `seasonal_average`_

    :keyword string outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
    :keyword int reach_id: the reach ID of COMID of a stream to be added to the plot title
    :keyword string drain_area: a string containing the area and units of the area upstream of this reach that will
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
    if not isinstance(seasonal, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or plotly or plotly_html')

    # we need to start at the first day of the year, pandas indexes from zero
    seasonal['day'] = pandas.to_datetime(seasonal['day'] + 1, format='%j')

    plot_data = {
        'reach_id': reach_id,
        'drain_area': drain_area,
        'x_day_number': seasonal['day'].tolist(),
        'y_flow': seasonal['streamflow_avg (m3/s)'].tolist(),
    }

    if outformat == 'json':
        return plot_data

    layout = Layout(
        title=__build_title('Daily Average Streamflow (Historic Simulation)', reach_id, drain_area),
        xaxis={
            'title': 'Date',
            'hoverformat': '%b %d (%j)',
            'tickformat': '%b'
        },
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * max(plot_data['y_flow'])]
        },
    )
    figure = Figure([Scatter(x=plot_data['x_day_number'], y=plot_data['y_flow'])], layout=layout)
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


def flow_duration_curve_plot(hist, **kwargs):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        hist (pandas.DataFrame): the csv response from `historic_simulation`_

    :keyword string outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
    :keyword int reach_id: the reach ID of COMID of a stream to be added to the plot title
    :keyword string drain_area: a string containing the area and units of the area upstream of this reach that will
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
    if not isinstance(hist, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or plotly or plotly_html')

    # process the hist dataframe to create the flow duration curve
    sorted_hist = hist.sort_values(by='streamflow (m3/s)', ascending=False)['streamflow (m3/s)'].tolist()

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

    layout = Layout(
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
    figure = Figure([Scatter(x=plot_data['x_probability'], y=plot_data['y_flow'])], layout=layout)
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


def probabilities_table(stats, ensembles, rperiods):
    """
    Processes the results of `forecast_stats`_ , `forecast_ensembles`_, and `return_periods`_ and uses jinja2 template
    rendering to generate html code that shows the probabilities of exceeding the return period flow on each day.

    Args:
        stats (pandas.DataFrame): the csv response from `forecast_stats`_
        ensembles (pandas.DataFrame): the csv response from `forecast_ensembles`_
        rperiods (pandas.DataFrame): the csv response from `return_periods`_

    :keyword string outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
    :keyword int reach_id: the reach ID of COMID of a stream to be added to the plot title
    :keyword string drain_area: a string containing the area and units of the area upstream of this reach that will
        be shown on the plot title

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.flow_duration_curve_plot(hist)
    """
    dates = stats['datetime'].tolist()
    startdate = dates[0]
    enddate = dates[-1]
    start_datetime = datetime.datetime.strptime(startdate, "%Y-%m-%d %H:00:00")
    span = datetime.datetime.strptime(enddate, "%Y-%m-%d %H:00:00") - start_datetime
    uniqueday = [start_datetime + datetime.timedelta(days=i) for i in range(span.days + 2)]
    # get the return periods for the stream reach
    rp2 = rperiods.iloc[3][0]
    rp10 = rperiods.iloc[2][0]
    rp20 = rperiods.iloc[1][0]

    # fill the lists of things used as context in rendering the template
    days = []
    r2 = []
    r10 = []
    r20 = []
    for i in range(len(uniqueday) - 1):  # (-1) omit the extra day used for reference only
        tmp = ensembles.loc[uniqueday[i]:uniqueday[i + 1]]
        days.append(uniqueday[i].strftime('%b %d'))
        num2 = 0
        num10 = 0
        num20 = 0
        for column in tmp:
            if any(i > rp20 for i in tmp[column].to_numpy()):
                num2 += 1
                num10 += 1
                num20 += 1
            elif any(i > rp10 for i in tmp[column].to_numpy()):
                num10 += 1
                num2 += 1
            elif any(i > rp2 for i in tmp[column].to_numpy()):
                num2 += 1
        r2.append(round(num2 * 100 / 52))
        r10.append(round(num10 * 100 / 52))
        r20.append(round(num20 * 100 / 52))

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates', 'probabilities_table.html'))
    with open(path) as template:
        return jinja2.Template(template.read()).render(days=days, r2=r2, r10=r10, r20=r20)


# UTILITY FUNCTIONS
def reach_to_region(reach_id):
    """
    returns the delineation region name corresponding to the range of numbers for a given reach_id.
    does not validate that the reach_id exists in the region, just associates a number to a name.

    Args:
        reach_id (int): the ID for a stream

    Return:
        region (str): the name of the delineated world region used by the API.

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
        ('indonesia-geoglows', 2000000),
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


def latlon_to_reach(lat, lon):
    """
    Uses the bounding boxes of all the regions to determine which comid_lat_lon_z csv(s) to read from

    Args:
        lat (int): a valid latitude
        lon (int): a valid longitude

    Return:
        stream_data (dict): a dictionary containing the reach_id as well as the name of the region and the distance
        from the provided lat and lon to the stream in units of degrees.

    Example:
        .. code-block:: python

            stream_data = latlon_to_reach(10, 50)
            {'reach_id': 123456, 'region': 'example_region-geoglows', 'distance': .05}
    """
    # create a shapely point for the querying
    point = Point(float(lon), float(lat))
    regions_to_check = []
    # store the best matching stream using a named tuple for easy comparisons/management
    StreamResult = namedtuple('Stream', 'reach_id, region, distance')
    stream_result = StreamResult(None, None, math.inf)
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'delineation_data'))

    # open the bounding boxes csv, figure out which regions the point lies within
    bb_csv = pandas.read_csv(os.path.join(base_path, 'bounding_boxes.csv'), index_col='region')
    for row in bb_csv.iterrows():
        bbox = box(row[1][0], row[1][1], row[1][2], row[1][3])
        if point.within(bbox):
            regions_to_check.append(row[0])

    # if there weren't any regions, return that there was an error
    if len(regions_to_check) == 0:
        return {"error": "This point is not within any of the supported delineation regions."}

    # switch the point because the csv's are lat/lon, backwards from what shapely expects (lon then lat)
    point = Point(float(lat), float(lon))

    # check the lat lon against each of the region csv's that we determined were an option
    for region in regions_to_check:
        # TEMPORARY until we figure out how to fix the west asia problem, skip it
        if region == 'west_asia-geoglows':
            pass

        # open the region csv, find the closest reach_id
        df = pandas.read_csv(os.path.join(base_path, region, 'comid_lat_lon_z.csv'), sep=',', header=0, index_col=0)
        points_df = df.loc[:, "Lat":"Lon"].apply(Point, axis=1)
        multi_pt = MultiPoint(points_df.tolist())
        nearest_pt = nearest_points(point, multi_pt)
        reach_id = int(points_df[points_df == nearest_pt[1]].index[0])

        # is this a better match than what we have? if so then replace the current selection
        distance = nearest_pt[0].distance(nearest_pt[1])
        if distance < stream_result.distance:
            stream_result = StreamResult(reach_id, region, distance)

    # there was only 1 option, return it
    if stream_result.distance > 0.11:
        return {"error": "Nearest river is more than ~10km away."}
    else:
        return dict(reach_id=stream_result.reach_id, region=stream_result.region, distance=stream_result.distance)


# MODULE AUXILIARY FUNCTIONS
def __build_title(base, reach_id, drain_area):
    if reach_id:
        base += '<br>Stream ID: ' + str(reach_id)
    if drain_area:
        base += '<br>Upstream Drainage Area: ' + str(drain_area)
    return base


def __rperiod_shapes(startdate, enddate, r2, r10, r20, y_max):
    return [
        go.layout.Shape(
            type='rect',
            x0=startdate,
            x1=enddate,
            y0=r2,
            y1=r10,
            line={'width': 0},
            opacity=.4,
            fillcolor='yellow'
        ),
        go.layout.Shape(
            type='rect',
            x0=startdate,
            x1=enddate,
            y0=r10,
            y1=r20,
            line={'width': 0},
            opacity=.4,
            fillcolor='red'
        ),
        go.layout.Shape(
            type='rect',
            x0=startdate,
            x1=enddate,
            y0=r20,
            y1=1.2 * y_max,
            line={'width': 0},
            opacity=.4,
            fillcolor='purple'
        ),
    ]


def __validate_api_params(reach_id, lat, lon, return_format):
    if not reach_id:
        if lat is not None and lon is not None:
            check = latlon_to_reach(lat, lon)
            if 'error' in check.keys():
                raise Exception('no reach_id was found near that lat/lon')
            reach_id = check['reach_id']
        else:
            raise Exception('provide a reach_id or both a lat and lon value')
    if return_format == 'request':
        return_format = 'csv'
    elif return_format not in ['csv', 'json', 'waterml']:
        raise Exception('choose csv, json, waterml, or request as return_format')
    # build and execute a request to the api with the user's parameters
    return {'reach_id': reach_id, 'return_format': return_format}
