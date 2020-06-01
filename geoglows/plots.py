import datetime
import json
import os

import hydrostats.data as hd
import jinja2
import pandas as pd
import plotly.graph_objs as go
import scipy.stats
from plotly.offline import plot as offline_plot

__all__ = ['hydroviewer', 'forecast_stats', 'forecast_records', 'forecast_ensembles', 'historic_simulation',
           'seasonal_average', 'flow_duration_curve', 'probabilities_table', 'return_periods_table',
           'corrected_historical', 'corrected_scatterplots', 'corrected_day_average', 'corrected_month_average',
           'corrected_volume_compare']


# FUNCTIONS THAT PROCESS THE RESULTS OF THE API INTO A PLOTLY PLOT OR DICTIONARY
def hydroviewer(recs: pd.DataFrame, stats: pd.DataFrame, ensem: pd.DataFrame, rperiods: pd.DataFrame = None,
                record_days: int = 7, outformat: str = 'plotly', titles: dict = False) -> go.Figure:
    """
    Creates the standard plot for a hydroviewer

    Args:
        recs: the response from forecast_records
        stats: the response from forecast_stats
        ensem: the response from forecast_ensembles
        rperiods: (optional) the response from return_periods
        outformat: (optional) either 'plotly' or 'plotly_html' (default plotly)
        record_days: (optional) number of days of forecast records to show before the start of the forecast
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.hydroviewer_plot(records, stats, rperiods)
    """
    if outformat not in ['plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick plotly or plotly_html')

    # determine the bounds of the plot on the x and y axis
    stats_dates = stats.index.tolist()
    # limit the forecast records to 7 days before the start of the forecast
    recs = recs[recs.index >= pd.to_datetime(stats_dates[0] - datetime.timedelta(days=record_days))]
    records_dates = recs.index.tolist()
    if len(records_dates) == 0:
        startdate = stats_dates[0]
        enddate = stats_dates[-1]
    else:
        startdate = min(records_dates[0], stats_dates[0])
        enddate = max(records_dates[-1], stats_dates[-1])
    max_flow = max(recs['streamflow_m^3/s'].max(), stats['flow_max_m^3/s'].max())

    # start building the plotly graph object
    figure = forecast_records(recs, outformat='plotly')
    for new_scatter in forecast_stats(stats, outformat='plotly_scatters'):
        figure.add_trace(new_scatter)

    # do the ensembles separately so we can group then and make only 1 legend entry
    ensemble_data = forecast_ensembles(ensem, outformat='json')
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
                          recs['streamflow_m^3/s'].max())
        for rp in _rperiod_scatters(startdate, enddate, rperiods, max_flow, max_visible):
            figure.add_trace(rp)

    figure.update_layout(
        title=_build_title('Forecasted Streamflow', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'range': [startdate, enddate]},
    )

    if outformat == 'plotly':
        return figure
    else:  # outformat == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )


def forecast_stats(stats: pd.DataFrame, rperiods: pd.DataFrame = None, titles: dict = False, outformat: str = 'plotly'):
    """
    Makes the streamflow data and optional metadata into a plotly plot

    Args:
        stats: the csv response from forecast_stats
        rperiods: the csv response from return_periods
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}
        outformat: 'json', 'plotly', 'plotly_scatters', or 'plotly_html' (default plotly)

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.forecast_plot(stats, rperiods)
    """
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    # Start processing the inputs
    dates = stats.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
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
        go.Scatter(name='Maximum & Minimum Flow',
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

        go.Scatter(name='High Resolution Forecast',
                   x=plot_data['x_hires'],
                   y=plot_data['high_res'],
                   line={'color': 'black'}, ),
        go.Scatter(name='Ensemble Average Flow',
                   x=plot_data['x_stats'],
                   y=plot_data['flow_avg'],
                   line=dict(color='blue'), ),
    ]
    scatter_plots += rperiod_scatters

    if outformat == 'plotly_scatters':
        return scatter_plots

    layout = go.Layout(
        title=_build_title('Forecasted Streamflow', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y', 'tickformat': '%b %d %Y'},
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


def forecast_ensembles(ensem: pd.DataFrame, rperiods: pd.DataFrame = None, titles: dict = False,
                       outformat: str = 'plotly'):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        ensem: the csv response from forecast_ensembles
        rperiods: the csv response from return_periods
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}
    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.ensembles_plot(ensembles, rperiods)
    """
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    # variables to determine the maximum flow and hold all the scatter plot lines
    max_flows = []
    scatter_plots = []

    # determine the threshold values for return periods and the start/end dates so we can plot them
    dates = ensem.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    # process the series' components and store them in a dictionary
    plot_data = {
        'x_1-51': ensem['ensemble_01_m^3/s'].dropna(axis=0).index.tolist(),
        'x_52': ensem['ensemble_52_m^3/s'].dropna(axis=0).index.tolist(),
    }

    # add a dictionary entry for each of the ensemble members. the key for each series is the integer ensemble number
    for ensemble in ensem.columns:
        plot_data[ensemble] = ensem[ensemble].dropna(axis=0).tolist()
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
        name='High Resolution Forecast',
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
        title=_build_title('Ensemble Predicted Streamflow', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y', 'tickformat': '%b %d %Y'},
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


def forecast_records(recs: pd.DataFrame, rperiods: pd.DataFrame = None, titles: dict = False,
                     outformat: str = 'plotly'):
    """
    Makes the streamflow saved forecast data and metadata into a plotly plot

    Args:
        recs: the csv response from forecast_records
        rperiods: the csv response from return_periods
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.record_plot(records, rperiods)
    """
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    # Start processing the inputs
    dates = recs.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'x_records': dates,
        'recorded_flows': recs['streamflow_m^3/s'].dropna(axis=0).tolist(),
        'y_max': max(recs['streamflow_m^3/s']),
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
        title=_build_title('Forecasted Streamflow Record', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'range': [startdate, enddate]},
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


def historic_simulation(hist: pd.DataFrame, rperiods: pd.DataFrame = None, titles: dict = False,
                        outformat: str = 'plotly'):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        hist: the csv response from historic_simulation
        rperiods: the csv response from return_periods
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.historic_plot(hist, rperiods)
    """
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    dates = hist.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
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

    scatter_plots = [go.Scatter(
        name='Historic Simulation',
        x=plot_data['x_datetime'],
        y=plot_data['y_flow'])
    ]
    scatter_plots += rperiod_scatters

    if outformat == 'plotly_scatters':
        return scatter_plots

    layout = go.Layout(
        title=_build_title('Historic Streamflow Simulation', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y', 'tickformat': '%Y'},
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
    raise ValueError('Invalid outformat chosen. Choose json, plotly, plotly_scatters, or plotly_html')


def seasonal_average(seas: pd.DataFrame, titles: dict = False, outformat: str = 'plotly'):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        seas: the csv response from seasonal_average
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.seasonal_plot(
                seasonal, reach_id=123456789, drain_area='123 km^2', outformat='json')
    """
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    plot_data = {
        'day_number': seas.index.tolist(),
        'average_flow': seas['streamflow_m^3/s'].tolist(),
        'max_flow': seas['max_flow'].tolist(),
        'min_flow': seas['min_flow'].tolist(),
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
        title=_build_title('Daily Average Streamflow (Historic Simulation)', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'range': [plot_data['day_number'][0], plot_data['day_number'][-1]],
               'hoverformat': '%b %d (%j)', 'tickformat': '%b'},
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
    raise ValueError('Invalid outformat chosen. Choose json, plotly, plotly_scatters, or plotly_html')


def flow_duration_curve(hist: pd.DataFrame, titles: dict = False, outformat: str = 'plotly'):
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        hist: the csv response from historic_simulation
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method

    Example:
        .. code-block:: python

            data = geoglows.streamflow.flow_duration_curve_plot(hist)
    """
    if outformat not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json, plotly, plotly_scatters, or plotly_html')

    # process the hist dataframe to create the flow duration curve
    sorted_hist = hist.sort_values(by='streamflow_m^3/s', ascending=False)['streamflow_m^3/s'].tolist()

    # ranks data from smallest to largest
    ranks = len(hist) - scipy.stats.rankdata(sorted_hist, method='average')

    # calculate probability of each rank
    prob = [(ranks[i] / (len(sorted_hist) + 1)) for i in range(len(sorted_hist))]

    plot_data = {
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
        title=_build_title('Flow Duration Curve', titles),
        xaxis={'title': 'Exceedence Probability'},
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
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
    raise ValueError('Invalid outformat chosen. Choose json, plotly, plotly_scatters, or plotly_html')


# STREAMFLOW HTML TABLES
def probabilities_table(stats: pd.DataFrame, ensem: pd.DataFrame, rperiods: pd.DataFrame) -> str:
    """
    Processes the results of forecast_stats , forecast_ensembles, and return_periods and uses jinja2 template
    rendering to generate html code that shows the probabilities of exceeding the return period flow on each day.

    Args:
        stats: the csv response from forecast_stats
        ensem: the csv response from forecast_ensembles
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
        tmp = ensem.loc[uniqueday[i]:uniqueday[i + 1]]
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
        string of html
    """

    # find the correct template to render
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates', 'return_periods_table.html'))
    # work on a copy of the dataframe so you dont ruin the original
    tmp = rperiods
    reach_id = str(tmp.index[0])
    js = json.loads(tmp.to_json())
    rp = {}
    for i in js:
        if i.startswith('return_period'):
            year = i.split('_')[-1]
            rp[f'{year} Year'] = js[i][reach_id]
        elif i == 'max_flow':
            rp['Max Simulated Flow'] = js[i][reach_id]

    rp = {key: round(value, 2) for key, value in sorted(rp.items(), key=lambda item: item[1])}

    with open(path) as template:
        return jinja2.Template(template.read()).render(reach_id=reach_id, rp=rp, colors=_plot_colors())


# BIAS CORRECTION PLOTS
def corrected_historical(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                         rperiods: pd.DataFrame = None, titles: dict = None,
                         outformat: str = 'plotly') -> go.Figure or str:
    """
    Creates a plot of corrected discharge, observered discharge, and simulated discharge

    Args:
        corrected: the response from the geoglows.bias.correct_historical_simulation function\
        simulated: the csv response from historic_simulation
        observed: the dataframe of observed data. Must have a datetime index and a single column of flow values
        rperiods: the csv response from return_periods
        outformat: either 'json', 'plotly', or 'plotly_html' (default plotly)
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}

    Returns:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    startdate = corrected.index[0]
    enddate = corrected.index[-1]

    plot_data = {
        'x_simulated': corrected.index.tolist(),
        'x_observed': observed.index.tolist(),
        'y_corrected': corrected.values.flatten(),
        'y_simulated': simulated.values.flatten(),
        'y_observed': observed.values.flatten(),
        'y_max': max(corrected.values.max(), observed.values.max(), simulated.values.max()),
    }
    if rperiods is not None:
        plot_data.update(rperiods.to_dict(orient='index').items())
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rperiods, plot_data['y_max'], plot_data['y_max'])
    else:
        rperiod_scatters = []

    if outformat == 'json':
        return plot_data

    scatters = [
        go.Scatter(
            name='Simulated Data',
            x=plot_data['x_simulated'],
            y=plot_data['y_simulated'],
            line=dict(color='red')
        ),
        go.Scatter(
            name='Observed Data',
            x=plot_data['x_observed'],
            y=plot_data['y_observed'],
            line=dict(color='blue')
        ),
        go.Scatter(
            name='Corrected Simulated Data',
            x=plot_data['x_simulated'],
            y=plot_data['y_corrected'],
            line=dict(color='green')
        ),
    ]
    scatters += rperiod_scatters

    layout = go.Layout(
        title=_build_title("Historical Simulation Comparison", titles),
        yaxis={'title': 'Discharge (m<sup>3</sup>/s)'},
        xaxis={'title': 'Date', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y', 'tickformat': '%Y'},
    )

    figure = go.Figure(data=scatters, layout=layout)
    if outformat == 'plotly':
        return figure
    if outformat == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid outformat chosen. Choose json, plotly, plotly_scatters, or plotly_html')


def corrected_scatterplots(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                           merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                           titles: dict = None, outformat: str = 'plotly') -> go.Figure or str:
    """
    Creates a plot of corrected discharge, observered discharge, and simulated discharge. This function uses
    hydrostats.data.merge_data on the 3 inputs. If you have already computed these because you are doing a full
    comparison of bias correction, you can provide them to save time

    Args:
        corrected: the response from the geoglows.bias.correct_historical_simulation function
        simulated: the csv response from historic_simulation
        observed: the dataframe of observed data. Must have a datetime index and a single column of flow values
        merged_sim_obs: (optional) if you have already computed it, hydrostats.data.merge_data(simulated, observed)
        merged_cor_obs: (optional) if you have already computed it, hydrostats.data.merge_data(corrected, observed)
        outformat: either 'plotly' or 'plotly_html' (default plotly)
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}

    Returns:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if corrected is False and simulated is False and observed is False:
        if merged_sim_obs is not False and merged_cor_obs is not False:
            pass  # if you provided the merged dataframes already, we use those
    else:
        # merge the datasets together
        merged_sim_obs = hd.merge_data(sim_df=simulated, obs_df=observed)
        merged_cor_obs = hd.merge_data(sim_df=corrected, obs_df=observed)

    # get the min/max values for plotting the 45 degree line
    min_value = min(min(merged_sim_obs.iloc[:, 1].values), min(merged_sim_obs.iloc[:, 0].values))
    max_value = max(max(merged_sim_obs.iloc[:, 1].values), max(merged_sim_obs.iloc[:, 0].values))

    # do a linear regression on both of the merged dataframes
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(merged_sim_obs.iloc[:, 0].values,
                                                                         merged_sim_obs.iloc[:, 1].values)
    slope2, intercept2, r_value2, p_value2, std_err2 = scipy.stats.linregress(merged_cor_obs.iloc[:, 0].values,
                                                                              merged_cor_obs.iloc[:, 1].values)
    scatter_sets = [
        go.Scatter(
            x=merged_sim_obs.iloc[:, 0].values,
            y=merged_sim_obs.iloc[:, 1].values,
            mode='markers',
            name='Original Data',
            marker=dict(color='#ef553b')
        ),
        go.Scatter(
            x=merged_cor_obs.iloc[:, 0].values,
            y=merged_cor_obs.iloc[:, 1].values,
            mode='markers',
            name='Corrected',
            marker=dict(color='#00cc96')
        ),
        go.Scatter(
            x=[min_value, max_value],
            y=[min_value, max_value],
            mode='lines',
            name='45 degree line',
            line=dict(color='black')
        ),
        go.Scatter(
            x=[min_value, max_value],
            y=[slope * min_value + intercept, slope * max_value + intercept],
            mode='lines',
            name=f'Y = {round(slope, 2)}x + {round(intercept, 2)} (Original)',
            line=dict(color='red')
        ),
        go.Scatter(
            x=[min_value, max_value],
            y=[slope2 * min_value + intercept2, slope2 * max_value + intercept2],
            mode='lines',
            name=f'Y = {round(slope2, 2)}x + {round(intercept2, 2)} (Corrected)',
            line=dict(color='green')
        )
    ]

    updatemenus = [
        dict(active=0,
             buttons=[dict(label='Linear Scale',
                           method='update',
                           args=[{'visible': [True, True]},
                                 {'title': 'Linear scale',
                                  'yaxis': {'type': 'linear'}}]),
                      dict(label='Log Scale',
                           method='update',
                           args=[{'visible': [True, True]},
                                 {'title': 'Log scale',
                                  'xaxis': {'type': 'log'},
                                  'yaxis': {'type': 'log'}}]),
                      ]
             )
    ]

    layout = go.Layout(title=_build_title('Bias Correction Scatter Plot', titles),
                       xaxis=dict(title='Simulated', ),
                       yaxis=dict(title='Observed', autorange=True),
                       showlegend=True, updatemenus=updatemenus)
    if outformat == 'plotly':
        return go.Figure(data=scatter_sets, layout=layout)
    elif outformat == 'plotly_html':
        return offline_plot(
            go.Figure(data=scatter_sets, layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid outformat chosen. Choose plotly or plotly_html')


def corrected_month_average(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                            merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                            titles: dict = None, outformat: str = 'plotly') -> go.Figure or str:
    """
    Calculates and plots the monthly average streamflow. This function uses
    hydrostats.data.merge_data on the 3 inputs. If you have already computed these because you are doing a full
    comparison of bias correction, you can provide them to save time

    Args:
        corrected: the response from the geoglows.bias.correct_historical_simulation function
        simulated: the csv response from historic_simulation
        observed: the dataframe of observed data. Must have a datetime index and a single column of flow values
        merged_sim_obs: (optional) if you have already computed it, hydrostats.data.merge_data(simulated, observed)
        merged_cor_obs: (optional) if you have already computed it, hydrostats.data.merge_data(corrected, observed)
        outformat: either 'plotly' or 'plotly_html' (default plotly)
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}

    Returns:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if corrected is False and simulated is False and observed is False:
        if merged_sim_obs is not False and merged_cor_obs is not False:
            pass  # if you provided the merged dataframes already, we use those
    else:
        # merge the datasets together
        merged_sim_obs = hd.merge_data(sim_df=simulated, obs_df=observed)
        merged_cor_obs = hd.merge_data(sim_df=corrected, obs_df=observed)
    monthly_avg = hd.monthly_average(merged_sim_obs)
    monthly_avg2 = hd.monthly_average(merged_cor_obs)

    scatters = [
        go.Scatter(x=monthly_avg.index, y=monthly_avg.iloc[:, 1].values, name='Observed Data'),
        go.Scatter(x=monthly_avg.index, y=monthly_avg.iloc[:, 0].values, name='Simulated Data'),
        go.Scatter(x=monthly_avg2.index, y=monthly_avg2.iloc[:, 0].values, name='Corrected Simulated Data'),
    ]

    layout = go.Layout(
        title=_build_title('Monthly Average Streamflow Comparison', titles),
        xaxis=dict(title='Month'), yaxis=dict(title='Discharge (m<sup>3</sup>/s)', autorange=True),
        showlegend=True)

    if outformat == 'plotly':
        return go.Figure(data=scatters, layout=layout)
    elif outformat == 'plotly_html':
        return offline_plot(
            go.Figure(data=scatters, layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid outformat chosen. Choose plotly or plotly_html')


def corrected_day_average(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                          merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                          titles: dict = None, outformat: str = 'plotly') -> go.Figure or str:
    """
    Calculates and plots the daily average streamflow. This function uses
    hydrostats.data.merge_data on the 3 inputs. If you have already computed these because you are doing a full
    comparison of bias correction, you can provide them to save time

    Args:
        corrected: the response from the geoglows.bias.correct_historical_simulation function
        simulated: the csv response from historic_simulation
        merged_sim_obs: (optional) if you have already computed it, hydrostats.data.merge_data(simulated, observed)
        merged_cor_obs: (optional) if you have already computed it, hydrostats.data.merge_data(corrected, observed)
        observed: the dataframe of observed data. Must have a datetime index and a single column of flow values
        outformat: either 'plotly' or 'plotly_html' (default plotly)
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}

    Returns:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if corrected is False and simulated is False and observed is False:
        if merged_sim_obs is not False and merged_cor_obs is not False:
            pass  # if you provided the merged dataframes already, we use those
    else:
        # merge the datasets together
        merged_sim_obs = hd.merge_data(sim_df=simulated, obs_df=observed)
        merged_cor_obs = hd.merge_data(sim_df=corrected, obs_df=observed)
    daily_avg = hd.daily_average(merged_sim_obs)
    daily_avg2 = hd.daily_average(merged_cor_obs)

    scatters = [
        go.Scatter(x=daily_avg.index, y=daily_avg.iloc[:, 1].values, name='Observed Data'),
        go.Scatter(x=daily_avg.index, y=daily_avg.iloc[:, 0].values, name='Simulated Data'),
        go.Scatter(x=daily_avg2.index, y=daily_avg2.iloc[:, 0].values, name='Corrected Simulated Data'),
    ]

    layout = go.Layout(
        title=_build_title('Daily Average Streamflow Comparison', titles),
        xaxis=dict(title='Days'), yaxis=dict(title='Discharge (m<sup>3</sup>/s)', autorange=True),
        showlegend=True)

    if outformat == 'plotly':
        return go.Figure(data=scatters, layout=layout)
    elif outformat == 'plotly_html':
        return offline_plot(
            go.Figure(data=scatters, layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid outformat chosen. Choose plotly or plotly_html')


def corrected_volume_compare(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                             merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                             titles: dict = None, outformat: str = 'plotly') -> go.Figure or str:
    """
    Calculates and plots the cumulative volume output on each of the 3 datasets provided. This function uses
    hydrostats.data.merge_data on the 3 inputs. If you have already computed these because you are doing a full
    comparison of bias correction, you can provide them to save time

    Args:
        corrected: the response from the geoglows.bias.correct_historical_simulation function
        simulated: the csv response from historic_simulation
        observed: the dataframe of observed data. Must have a datetime index and a single column of flow values
        merged_sim_obs: (optional) if you have already computed it, hydrostats.data.merge_data(simulated, observed)
        merged_cor_obs: (optional) if you have already computed it, hydrostats.data.merge_data(corrected, observed)
        outformat: either 'plotly' or 'plotly_html' (default plotly)
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}

    Returns:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if corrected is False and simulated is False and observed is False:
        if merged_sim_obs is not False and merged_cor_obs is not False:
            pass  # if you provided the merged dataframes already, we use those
    else:
        # merge the datasets together
        merged_sim_obs = hd.merge_data(sim_df=simulated, obs_df=observed)
        merged_cor_obs = hd.merge_data(sim_df=corrected, obs_df=observed)

    sim_array = merged_sim_obs.iloc[:, 0].values
    obs_array = merged_sim_obs.iloc[:, 1].values
    corr_array = merged_cor_obs.iloc[:, 0].values

    sim_volume_dt = sim_array * 0.0864
    obs_volume_dt = obs_array * 0.0864
    corr_volume_dt = corr_array * 0.0864

    sim_volume_cum = []
    obs_volume_cum = []
    corr_volume_cum = []
    sum_sim = 0
    sum_obs = 0
    sum_corr = 0

    for i in sim_volume_dt:
        sum_sim = sum_sim + i
        sim_volume_cum.append(sum_sim)

    for j in obs_volume_dt:
        sum_obs = sum_obs + j
        obs_volume_cum.append(sum_obs)

    for k in corr_volume_dt:
        sum_corr = sum_corr + k
        corr_volume_cum.append(sum_corr)

    observed_volume = go.Scatter(x=merged_sim_obs.index, y=obs_volume_cum, name='Observed', )
    simulated_volume = go.Scatter(x=merged_sim_obs.index, y=sim_volume_cum, name='Simulated', )
    corrected_volume = go.Scatter(x=merged_cor_obs.index, y=corr_volume_cum, name='Corrected Simulated', )

    layout = go.Layout(
        title=_build_title('Cumulative Volume Comparison', titles),
        xaxis=dict(title='Datetime', ), yaxis=dict(title='Volume (m<sup>3</sup>)', autorange=True),
        showlegend=True)

    if outformat == 'plotly':
        return go.Figure(data=[observed_volume, simulated_volume, corrected_volume], layout=layout)
    elif outformat == 'plotly_html':
        return offline_plot(
            go.Figure(data=[observed_volume, simulated_volume, corrected_volume], layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid outformat chosen. Choose plotly or plotly_html')


# PLOTTING AUXILIARY FUNCTIONS
def _build_title(base, title_headers):
    if not title_headers:
        return base
    if 'bias_corrected' in title_headers.keys():
        base = 'Bias Corrected ' + base
    for head in title_headers:
        if head == 'bias_corrected':
            continue
        base += f'<br>{head}: {title_headers[head]}'
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

    def template(name, y, color, fill='toself'):
        return go.Scatter(
            name=name,
            x=x_vals,
            y=y,
            legendgroup='returnperiods',
            fill=fill,
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
            template('Return Periods', (rmax, rmax, rmax, rmax), 'rgba(0,0,0,0)', fill='none'),
            template(f'2 Year: {r2}', (r2, r2, r5, r5), colors['2 Year']),
            template(f'5 Year: {r5}', (r5, r5, r10, r10), colors['5 Year']),
            template(f'10 Year: {r10}', (r10, r10, r25, r25), colors['10 Year']),
            template(f'25 Year: {r25}', (r25, r25, r50, r50), colors['25 Year']),
            template(f'50 Year: {r50}', (r50, r50, r100, r100), colors['50 Year']),
            template(f'100 Year: {r100}', (r100, r100, rmax, rmax), colors['100 Year']),
        ]
