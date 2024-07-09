import numpy as np
import pandas as pd
import plotly.graph_objs as go
import scipy.stats

from .format_tools import build_title, timezone_label
from .plotly_helpers import _rperiod_scatters

__all__ = [
    'retrospective',
    'daily_averages',
    'monthly_averages',
    'annual_averages',
    'daily_variance',
    'flow_duration_curve',
]


def retrospective(df: pd.DataFrame, *, rp_df: pd.DataFrame = None, plot_titles: dict = None, ) -> go.Figure:
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        df: the csv response from historic_simulation
        rp_df: the csv response from return_periods
        plot_titles: (dict) Extra info to show on the title of the plot. For example:
            {'River ID': 1234567, 'Drainage Area': '1000km^2'}

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    dates = df.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'x_datetime': dates,
        'y_flow': df.values.flatten(),
        'y_max': df.values.max(),
    }
    if rp_df is not None:
        plot_data.update(rp_df.to_dict(orient='index').items())
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rp_df, plot_data['y_max'], plot_data['y_max'])
    else:
        rperiod_scatters = []

    scatter_plots = [go.Scatter(
        name='Retrospective Simulation',
        x=plot_data['x_datetime'],
        y=plot_data['y_flow'])
    ]
    scatter_plots += rperiod_scatters

    layout = go.Layout(
        title=build_title('Retrospective Streamflow Simulation', plot_titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={
            'title': timezone_label(df.index.tz),
            'range': [startdate, enddate],
            'hoverformat': '%d %b %Y',
            'tickformat': '%Y'
        },
    )
    return go.Figure(scatter_plots, layout=layout)


def daily_averages(dayavg: pd.DataFrame, plot_titles: list = None, plot_type: str = 'plotly') -> go.Figure:
    """
    Makes the daily_averages data and metadata into a plotly plot

    Args:
        dayavg: the csv response from daily_averages
        plot_titles: (dict) Extra info to show on the title of the plot. For example:
            {'River ID': 1234567, 'Drainage Area': '1000km^2'}
        plot_type: either 'plotly', or 'html' (default plotly)

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if plot_type not in ['plotly_scatters', 'plotly', 'html']:
        raise ValueError('invalid plot_type specified. pick plotly, plotly_scatters, or html')

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
        title=build_title('Daily Average Streamflow (Simulated)', plot_titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date', 'hoverformat': '%b %d', 'tickformat': '%b'},
    )
    return go.Figure(scatter_plots, layout=layout)


def monthly_averages(monavg: pd.DataFrame, plot_titles: list = None,
                     plot_type: str = 'plotly') -> go.Figure:
    """
    Makes the daily_averages data and metadata into a plotly plot

    Args:
        monavg: the csv response from monthly_averages
        plot_titles: (dict) Extra info to show on the title of the plot. For example:
            {'River ID': 1234567, 'Drainage Area': '1000km^2'}
        plot_type: either 'plotly', or 'html' (default plotly)

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if plot_type not in ['plotly_scatters', 'plotly', 'html']:
        raise ValueError('invalid plot_type specified. pick plotly, plotly_scatters, or html')

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
        title=build_title('Monthly Average Streamflow (Simulated)', plot_titles=plot_titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)'},
        xaxis={'title': 'Month'},
    )
    return go.Figure(scatter_plots, layout=layout)


def annual_averages(df: pd.DataFrame, *, plot_titles: list = None, decade_averages: bool = False) -> go.Figure:
    """
    Makes the annual_averages data and metadata into a plotly plot

    Args:
        df: the csv response from annual_averages
        plot_titles: (dict) Extra info to show on the title of the plot. For example:
            {'River ID': 1234567, 'Drainage Area': '1000km^2'}
        decade_averages: (bool) if True, will plot the average flow for each decade

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    scatter_plots = [
        go.Scatter(
            name='Average Annual Flow',
            x=df.index.tolist(),
            y=df.values.flatten(),
            line=dict(color='blue')
        ),
    ]

    if decade_averages:
        # get a list of decades covered by the data in the index
        first_year = str(int(df.index[0]))[:-1] + '0'
        last_year = str(int(df.index[-1]))[:-1] + '9'
        first_year = int(first_year)
        last_year = int(last_year)
        decades = [decade for decade in range(int(first_year), int(last_year) + 1, 10)]
        for idx, decade in enumerate(decades):
            decade_values = df[np.logical_and(df.index.astype(int) >= decade, df.index.astype(int) < decade + 10)]
            mean_flow = decade_values.values.flatten().mean()
            scatter_plots.append(
                go.Scatter(
                    name=f'{decade}s: {mean_flow:.2f} m<sup>3</sup>/s',
                    x=[decade_values.index[0], decade_values.index[-1]],
                    y=mean_flow * np.ones(2),
                    line=dict(color='red'),
                    hoverinfo='name',
                    legendgroup='decade_averages',
                    legendgrouptitle=dict(text='Decade Averages')
                )
            )

    layout = go.Layout(
        title=build_title('Annual Average Streamflow (Simulated)', plot_titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)'},
        xaxis={'title': 'Year'},
    )
    return go.Figure(scatter_plots, layout=layout)


def flow_duration_curve(df: pd.DataFrame, plot_titles: dict = None, plot_type: str = 'plotly') -> go.Figure:
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
        df: the dataframe response from data.retrospective
        plot_titles: (dict) Extra info to show on the title of the plot. For example:
            {'River ID': 1234567, 'Drainage Area': '1000km^2'}
        plot_type: either 'json', 'plotly', or 'html' (default plotly)

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    if plot_type not in ['json', 'plotly_scatters', 'plotly', 'html']:
        raise ValueError('invalid plot_type specified. pick json, plotly, plotly_scatters, or html')

    # process the hist dataframe to create the flow duration curve
    sorted_hist = df.values.flatten()
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
        title=build_title('Flow Duration Curve', plot_titles),
        xaxis={'title': 'Exceedence Probability'},
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
    )
    return go.Figure(scatter_plots, layout=layout)


def daily_stats(df: pd.DataFrame, *, plot_titles: dict = None, plot_type: str = 'plotly') -> go.Figure:
    """
    Plots a graph with statistics for each day of year

    Args:
        df: dataframe of values to plot
        plot_titles: (dict) Extra info to show on the title of the plot. For example:
            {'River ID': 1234567, 'Drainage Area': '1000km^2'}
        plot_type: either 'plotly' (python object, default), 'plotly_scatters', or 'html'

    returns:
        plot of the graph of the low flows
    """

    stats_df = daily_stats(df)

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
        title=build_title('Daily Average Streamflow (Simulated)', plot_titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': timezone_label(df.index.tz), 'hoverformat': '%b %d', 'tickformat': '%b'},
    )
    return go.Figure(data=data, layout=layout)


def daily_variance(daily_variance: pd.DataFrame, plot_titles: list = None, plot_type: str = 'plotly') -> go.Figure:
    """
    A dataframe of daily variances computed by the geoglows.analysis.compute_daily_variance function

    Args:
      daily_variance: dataframe of values to plot coming from geoglows.analysis.compute_daily_variance
      plot_titles: (dict) Extra info to show on the title of the plot. For example:
        {'River ID': 1234567, 'Drainage Area': '1000km^2'}
      plot_type: either 'plotly' (python object, default), 'plotly_scatters', or 'html'

    returns:
      plot of standard deviation and plot of the graph of the low flows
    """
    data = [
        go.Scatter(
            x=daily_variance['date'],
            y=daily_variance['flow_std'],
            name="Daily Standard Deviation"
        ),
    ]
    if plot_type == 'plotly_scatters':
        return data
    return go.Figure(data=data, layout=go.Layout(build_title('Daily Flow Standard Deviation', plot_titles)))
