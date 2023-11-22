import datetime
import json
import os

import hydrostats.data as hd
import jinja2
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import scipy.stats
from plotly.offline import plot as offline_plot

from .analysis import compute_daily_statistics

__all__ = [
    'forecast',
    'forecast_stats',
    'forecast_records',
    'forecast_ensembles',

    'retrospective',
    'daily_averages',
    'monthly_averages',
    # todo 'annual_averages',

    'daily_variance',
    'flow_duration_curve',
    'probabilities_table',
    'return_periods_table',

    'corrected_historical',
    'corrected_scatterplots',
    'corrected_day_average',
    'corrected_month_average',
    'corrected_volume_compare',
    'daily_stats'
]


def forecast(df: pd.DataFrame, *,
             rp_df: pd.DataFrame = None,
             plot_titles: list = None, ) -> go.Figure:
    """
    Plots forecasted streamflow and optional return periods
    Args:
        df: the dataframe response from geoglows.data.forecast
        rp_df: optional dataframe of return period data
        plot_titles: optional list of strings to include in the figure title. each list item will be on a new line.

    Returns:
        go.Figure
    """
    scatter_traces = [
        go.Scatter(
            x=df.index,
            y=df['flow_median_cms'],
            name='Streamflow (Median)',
            line=dict(color='black'),
        ),
        go.Scatter(
            name='Uncertainty Bounds',
            x=np.concatenate([df.index.values, df.index.values[::-1]]),
            y=np.concatenate([df['flow_uncertainty_upper_cms'], df['flow_uncertainty_lower_cms'][::-1]]),
            legendgroup='uncertainty',
            showlegend=True,
            fill='toself',
            line=dict(color='lightblue', dash=None)
        ),
        go.Scatter(
            name='Uncertainty Upper Bounds (80%)',
            x=df.index,
            y=df['flow_uncertainty_upper_cms'],
            legendgroup='uncertainty',
            showlegend=False,
            line=dict(color='lightblue', dash='dash')
        ),
        go.Scatter(
            name='Uncertainty Lower Bounds (20%)',
            x=df.index,
            y=df['flow_uncertainty_lower_cms'],
            legendgroup='uncertainty',
            showlegend=False,
            line=dict(color='lightblue', dash='dash')
        ),
    ]

    if rp_df is not None:
        # todo
        ...

    layout = go.Layout(
        title=_build_title('Forecasted Streamflow', plot_titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date (UTC +0:00)', 'range': [df.index[0], df.index[-1]]},
    )

    return go.Figure(scatter_traces, layout=layout)


def forecast_stats(df: pd.DataFrame, *,
                   rp_df: pd.DataFrame = None,
                   plot_titles: list = False,
                   hide_maxmin: bool = False, ) -> go.Figure:
    """
    Makes the streamflow data and optional metadata into a plotly plot

    Args:
        *:
        df: the csv response from forecast_stats
        rp_df: the csv response from return_periods
        plot_titles: a list of strings to place in the figure title. each list item will be on a new line.
        hide_maxmin: Choose to hide the max/min envelope by default

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    # Start processing the inputs
    dates = df.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'x_stats': df['flow_avg_cms'].dropna(axis=0).index.tolist(),
        'x_hires': df['high_res_cms'].dropna(axis=0).index.tolist(),
        'y_max': max(df['flow_max_cms']),
        'flow_max': list(df['flow_max_cms'].dropna(axis=0)),
        'flow_75%': list(df['flow_75p_cms'].dropna(axis=0)),
        'flow_avg': list(df['flow_avg_cms'].dropna(axis=0)),
        'flow_med': list(df['flow_med_cms'].dropna(axis=0)),
        'flow_25%': list(df['flow_25p_cms'].dropna(axis=0)),
        'flow_min': list(df['flow_min_cms'].dropna(axis=0)),
        'high_res': list(df['high_res_cms'].dropna(axis=0)),
    }

    maxmin_visible = 'legendonly' if hide_maxmin else True
    scatter_plots = [
        # Plot together so you can use fill='toself' for the shaded box, also separately so the labels appear
        go.Scatter(name='Maximum & Minimum Flow',
                   x=plot_data['x_stats'] + plot_data['x_stats'][::-1],
                   y=plot_data['flow_max'] + plot_data['flow_min'][::-1],
                   legendgroup='boundaries',
                   fill='toself',
                   visible=maxmin_visible,
                   line=dict(color='lightblue', dash='dash')),
        go.Scatter(name='Maximum',
                   x=plot_data['x_stats'],
                   y=plot_data['flow_max'],
                   legendgroup='boundaries',
                   visible=maxmin_visible,
                   showlegend=False,
                   line=dict(color='darkblue', dash='dash')),
        go.Scatter(name='Minimum',
                   x=plot_data['x_stats'],
                   y=plot_data['flow_min'],
                   legendgroup='boundaries',
                   visible=maxmin_visible,
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

        go.Scatter(name='Higher Time Step Forecast',
                   x=plot_data['x_hires'],
                   y=plot_data['high_res'],
                   visible=True,
                   line={'color': 'black'}, ),

        go.Scatter(name='Average Flow',
                   x=plot_data['x_stats'],
                   y=plot_data['flow_avg'],
                   line=dict(color='blue'), ),
        go.Scatter(name='Median Flow',
                   x=plot_data['x_stats'],
                   y=plot_data['flow_med'],
                   line=dict(color='red'), ),
    ]
    if rp_df is not None:
        plot_data.update(rp_df.to_dict(orient='index').items())
        max_visible = max(max(plot_data['flow_75%']), max(plot_data['flow_avg']), max(plot_data['high_res']))
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rp_df, plot_data['y_max'], max_visible)
        scatter_plots += rperiod_scatters

    layout = go.Layout(
        title=_build_title('Forecasted Streamflow', plot_titles),
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 'auto']
        },
        xaxis={
            'title': 'Date (UTC +0:00)',
            'range': [startdate, enddate],
            'hoverformat': '%b %d %Y',
            'tickformat': '%b %d %Y'
        },
    )

    return go.Figure(scatter_plots, layout=layout)


def forecast_ensembles(df: pd.DataFrame, *,
                       rp_df: pd.DataFrame = None,
                       plot_titles: dict = False, ) -> go.Figure:
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        *:
        df: the dataframe response from geoglows.data.forecast_ensembles
        rp_df: the csv response from return_periods
        plot_titles: a list of strings to place in the figure title. each list item will be on a new line.
    Return:
         go.Figure
    """
    # variables to determine the maximum flow and hold all the scatter plot lines
    max_flows = []
    scatter_plots = []

    # determine the threshold values for return periods and the start/end dates so we can plot them
    dates = df.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    # process the series' components and store them in a dictionary
    plot_data = {
        'x_1-51': df['ensemble_01_m^3/s'].dropna(axis=0).index.tolist(),
        'x_52': df['ensemble_52_m^3/s'].dropna(axis=0).index.tolist(),
    }

    # add a dictionary entry for each of the ensemble members. the key for each series is the integer ensemble number
    for ensemble in df.columns:
        plot_data[ensemble] = df[ensemble].dropna(axis=0).tolist()
        max_flows.append(max(plot_data[ensemble]))
    plot_data['y_max'] = max(max_flows)

    if rp_df is not None:
        plot_data.update(rp_df.to_dict(orient='index').items())
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rp_df, plot_data['y_max'])
    else:
        rperiod_scatters = []

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

    # define a layout for the plot
    layout = go.Layout(
        title=_build_title('Ensemble Predicted Streamflow', plot_titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date (UTC +0:00)', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y',
               'tickformat': '%b %d %Y'},
    )
    return go.Figure(scatter_plots, layout=layout)


def forecast_records(recs: pd.DataFrame, rperiods: pd.DataFrame = None, titles: dict = False,
                     plot_type: str = 'plotly') -> go.Figure:
    """
    Makes the streamflow saved forecast data and metadata into a plotly plot

    Args:
        recs: the csv response from forecast_records
        rperiods: the csv response from return_periods
        plot_type: either 'json', 'plotly', or 'plotly_html' (default plotly)
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if plot_type not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid plot_type specified. pick json, plotly, plotly_scatters, or plotly_html')

    # Start processing the inputs
    dates = recs.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'x_records': dates,
        'recorded_flows': recs.dropna(axis=0).values.flatten(),
        'y_max': max(recs.values),
    }
    if rperiods is not None:
        plot_data.update(rperiods.to_dict(orient='index').items())
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rperiods, plot_data['y_max'], plot_data['y_max'])
    else:
        rperiod_scatters = []
    if plot_type == 'json':
        return plot_data

    scatter_plots = [go.Scatter(
        name='Previous Forecast Average',
        x=plot_data['x_records'],
        y=plot_data['recorded_flows'],
        line=dict(color='gold'),
    )] + rperiod_scatters

    if plot_type == 'plotly_scatters':
        return scatter_plots

    layout = go.Layout(
        title=_build_title('Forecasted Streamflow Record', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date (UTC +0:00)', 'range': [startdate, enddate]},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    if plot_type == 'plotly':
        return figure
    if plot_type == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    return


def retrospective(retro: pd.DataFrame, rperiods: pd.DataFrame = None, titles: dict = False,
                  plot_type: str = 'plotly') -> go.Figure:
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        retro: the csv response from historic_simulation
        rperiods: the csv response from return_periods
        plot_type: either 'json', 'plotly', or 'plotly_html' (default plotly)
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if plot_type not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid plot_type specified. pick json, plotly, plotly_scatters, or plotly_html')

    dates = retro.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'x_datetime': dates,
        'y_flow': retro.values.flatten(),
        'y_max': max(retro.values),
    }
    if rperiods is not None:
        plot_data.update(rperiods.to_dict(orient='index').items())
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rperiods, plot_data['y_max'], plot_data['y_max'])
    else:
        rperiod_scatters = []

    if plot_type == 'json':
        return plot_data

    scatter_plots = [go.Scatter(
        name='Retrospective Simulation',
        x=plot_data['x_datetime'],
        y=plot_data['y_flow'])
    ]
    scatter_plots += rperiod_scatters

    if plot_type == 'plotly_scatters':
        return scatter_plots

    layout = go.Layout(
        title=_build_title('Historical Streamflow Simulation', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date (UTC +0:00)', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y',
               'tickformat': '%Y'},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    if plot_type == 'plotly':
        return figure
    if plot_type == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose json, plotly, plotly_scatters, or plotly_html')


def daily_averages(dayavg: pd.DataFrame, titles: dict = False, plot_type: str = 'plotly') -> go.Figure:
    """
    Makes the daily_averages data and metadata into a plotly plot

    Args:
        dayavg: the csv response from daily_averages
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}
        plot_type: either 'plotly', or 'plotly_html' (default plotly)

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if plot_type not in ['plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid plot_type specified. pick plotly, plotly_scatters, or plotly_html')

    scatter_plots = [
        go.Scatter(
            name='Average Daily Flow',
            x=dayavg.index.tolist(),
            y=dayavg.values.flatten(),
            line=dict(color='blue')
        ),
    ]
    if plot_type == 'plotly_scatters':
        return scatter_plots
    layout = go.Layout(
        title=_build_title('Daily Average Streamflow (Simulated)', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date (UTC +0:00)', 'hoverformat': '%b %d', 'tickformat': '%b'},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    if plot_type == 'plotly':
        return figure
    if plot_type == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose plotly, plotly_scatters, or plotly_html')


def daily_variance(daily_variance: pd.DataFrame, titles: dict = None, plot_type: str = 'plotly') -> go.Figure:
    """
    A dataframe of daily variances computed by the geoglows.analysis.compute_daily_variance function

    Args:
      daily_variance: dataframe of values to plot coming from geoglows.analysis.compute_daily_variance
      titles: (dict) Extra info to show on the title of the plot. For example:
        {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}
      plot_type: either 'plotly' (python object, default), 'plotly_scatters', or 'plotly_html'

    returns:
      plot of standard deviation and plot of the graph of the low flows
    """
    data = [
        go.Scatter(
            x=daily_variance['date'],
            y=daily_variance['flow_std'],
            name="Daily Standard Deviation"
        )
    ]
    if plot_type == 'plotly_scatters':
        return data
    figure = go.Figure(data=data, layout=go.Layout(_build_title('Daily Flow Standard Deviation', titles)))
    if plot_type == 'plotly':
        return figure
    elif plot_type == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose plotly or plotly_html')


def daily_stats(hist: pd.DataFrame, titles: dict = None, plot_type: str = 'plotly') -> go.Figure:
    """
    Plots a graph with statistics for each day of year

    Args:
        hist: dataframe of values to plot
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}
        plot_type: either 'plotly' (python object, default), 'plotly_scatters', or 'plotly_html'

    returns:
        plot of the graph of the low flows
    """

    stats_df = compute_daily_statistics(hist)

    data = [
        go.Scatter(
            x=stats_df.index.tolist(),
            y=stats_df[column].tolist(),
            name=column
        ) for column in stats_df.columns
    ]

    if plot_type == 'plotly_scatters':
        return data
    layout = go.Layout(
        title=_build_title('Daily Average Streamflow (Simulated)', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date (UTC +0:00)', 'hoverformat': '%b %d', 'tickformat': '%b'},
    )
    figure = go.Figure(data=data, layout=layout)
    if plot_type == 'plotly':
        return figure
    elif plot_type == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose plotly or plotly_html')


def monthly_averages(monavg: pd.DataFrame, titles: dict = False, plot_type: str = 'plotly') -> go.Figure:
    """
    Makes the daily_averages data and metadata into a plotly plot

    Args:
        monavg: the csv response from monthly_averages
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}
        plot_type: either 'plotly', or 'plotly_html' (default plotly)

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if plot_type not in ['plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid plot_type specified. pick plotly, plotly_scatters, or plotly_html')

    scatter_plots = [
        go.Scatter(
            name='Average Monthly Flow',
            x=pd.to_datetime(monavg.index, format='%m').strftime('%B'),
            y=monavg.values.flatten(),
            line=dict(color='blue')
        ),
    ]
    if plot_type == 'plotly_scatters':
        return scatter_plots
    layout = go.Layout(
        title=_build_title('Monthly Average Streamflow (Simulated)', titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)'},
        xaxis={'title': 'Month'},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    if plot_type == 'plotly':
        return figure
    if plot_type == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose plotly, plotly_scatters, or plotly_html')


def flow_duration_curve(hist: pd.DataFrame, titles: dict = False, plot_type: str = 'plotly') -> go.Figure:
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        hist: the csv response from historic_simulation
        titles: (dict) Extra info to show on the title of the plot. For example:
            {'Reach ID': 1234567, 'Drainage Area': '1000km^2'}
        plot_type: either 'json', 'plotly', or 'plotly_html' (default plotly)

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if plot_type not in ['json', 'plotly_scatters', 'plotly', 'plotly_html']:
        raise ValueError('invalid plot_type specified. pick json, plotly, plotly_scatters, or plotly_html')

    # process the hist dataframe to create the flow duration curve
    sorted_hist = hist.values.flatten()
    sorted_hist.sort()

    # ranks data from smallest to largest
    ranks = len(sorted_hist) - scipy.stats.rankdata(sorted_hist, method='average')

    # calculate probability of each rank
    prob = [(ranks[i] / (len(sorted_hist) + 1)) for i in range(len(sorted_hist))]

    plot_data = {
        'x_probability': prob,
        'y_flow': sorted_hist,
        'y_max': sorted_hist[0],
    }

    if plot_type == 'json':
        return plot_data

    scatter_plots = [
        go.Scatter(
            name='Flow Duration Curve',
            x=plot_data['x_probability'],
            y=plot_data['y_flow'])
    ]
    if plot_type == 'plotly_scatters':
        return scatter_plots
    layout = go.Layout(
        title=_build_title('Flow Duration Curve', titles),
        xaxis={'title': 'Exceedence Probability'},
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    if plot_type == 'plotly':
        return figure
    if plot_type == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose json, plotly, plotly_scatters, or plotly_html')


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
            column_max = tmp[column].to_numpy().max()
            if column_max > rp100:
                num100 += 1
            if column_max > rp50:
                num50 += 1
            if column_max > rp25:
                num25 += 1
            if column_max > rp10:
                num10 += 1
            if column_max > rp5:
                num5 += 1
            if column_max > rp2:
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
                         plot_type: str = 'plotly') -> go.Figure or str:
    """
    Creates a plot of corrected discharge, observered discharge, and simulated discharge

    Args:
        corrected: the response from the geoglows.bias.correct_historical_simulation function\
        simulated: the csv response from historic_simulation
        observed: the dataframe of observed data. Must have a datetime index and a single column of flow values
        rperiods: the csv response from return_periods
        plot_type: either 'plotly', or 'plotly_html' (default plotly)
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

    if plot_type == 'json':
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
            line=dict(color='#00cc96')
        ),
    ]
    scatters += rperiod_scatters

    layout = go.Layout(
        title=_build_title("Historical Simulation Comparison", titles),
        yaxis={'title': 'Discharge (m<sup>3</sup>/s)'},
        xaxis={'title': 'Date (UTC +0:00)', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y',
               'tickformat': '%Y'},
    )

    figure = go.Figure(data=scatters, layout=layout)
    if plot_type == 'plotly':
        return figure
    if plot_type == 'plotly_html':
        return offline_plot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose json, plotly, plotly_scatters, or plotly_html')


def corrected_scatterplots(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                           merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                           titles: dict = None, plot_type: str = 'plotly') -> go.Figure or str:
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
        plot_type: either 'plotly' or 'plotly_html' (default plotly)
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
    if plot_type == 'plotly':
        return go.Figure(data=scatter_sets, layout=layout)
    elif plot_type == 'plotly_html':
        return offline_plot(
            go.Figure(data=scatter_sets, layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose plotly or plotly_html')


def corrected_month_average(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                            merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                            titles: dict = None, plot_type: str = 'plotly') -> go.Figure or str:
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
        plot_type: either 'plotly' or 'plotly_html' (default plotly)
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

    if plot_type == 'plotly':
        return go.Figure(data=scatters, layout=layout)
    elif plot_type == 'plotly_html':
        return offline_plot(
            go.Figure(data=scatters, layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose plotly or plotly_html')


def corrected_day_average(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                          merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                          titles: dict = None, plot_type: str = 'plotly') -> go.Figure or str:
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
        plot_type: either 'plotly' or 'plotly_html' (default plotly)
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

    if plot_type == 'plotly':
        return go.Figure(data=scatters, layout=layout)
    elif plot_type == 'plotly_html':
        return offline_plot(
            go.Figure(data=scatters, layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose plotly or plotly_html')


def corrected_volume_compare(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                             merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                             titles: dict = None, plot_type: str = 'plotly') -> go.Figure or str:
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
        plot_type: either 'plotly' or 'plotly_html' (default plotly)
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

    if plot_type == 'plotly':
        return go.Figure(data=[observed_volume, simulated_volume, corrected_volume], layout=layout)
    elif plot_type == 'plotly_html':
        return offline_plot(
            go.Figure(data=[observed_volume, simulated_volume, corrected_volume], layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    raise ValueError('Invalid plot_type chosen. Choose plotly or plotly_html')


# PLOTTING AUXILIARY FUNCTIONS
def _build_title(main_title, plot_titles: list):
    if not title_headers:
        return main_title
    if 'bias_corrected' in title_headers.keys():
        main_title = 'Bias Corrected ' + main_title
    for header_item in title_headers:
        if head == 'bias_corrected':
            continue
        main_title += f'<br>{head}: {title_headers[head]}'
    return main_title


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


def _rperiod_scatters(startdate: str, enddate: str, rperiods: pd.DataFrame, y_max: float, max_visible: float = 0,
                      visible: bool = None):
    colors = _plot_colors()
    x_vals = (startdate, enddate, enddate, startdate)
    r2 = int(rperiods['return_period_2'].values[0])
    if visible is None:
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


def plot_low_flows(data: pd.DataFrame, rps: tuple = (2, 5, 10, 25, 50)):
    """
    Plots the graph for the standard deviation over a year and the graph of low flows by day of the year

    Args:
        data: dataframe of values to plot
        rps: tuple for the return periods - default is (2, 5, 10, 25, 50)

    returns:
        plot of the graph of the low flows
    """
    data['datetime'] = pd.to_datetime(data['datetime'])
    streamflow_data = pd.DataFrame()
    streamflow_data['streamflow'] = data['streamflow_m^3/s']
    streamflow_data['day'] = data['datetime'].dt.strftime('%m-%d')
    daily_averages = streamflow_data.groupby('day').mean()
    averages = [
        go.Scatter(
            x=daily_averages.index,
            y=daily_averages['streamflow'],
            name="daily-averages"
        )
    ]
    layout = go.Layout(xaxis={'type': 'category'}, title="Low flows by day of year")
    plot = go.Figure(data=averages, layout=layout)
    for rp in rps:
        quantile = streamflow_data.groupby('day').quantile(1 / rp)
        plot.add_trace(
            go.Scatter(
                x=daily_averages.index,
                y=quantile['streamflow'],
                name=f'{rp}_year'
            )
        )
    return plot
