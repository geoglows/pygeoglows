import numpy as np
import pandas as pd
import plotly.graph_objects as go

from .format_tools import build_title
from .plotly_helpers import _rperiod_scatters

__all__ = [
    'forecast',
    'forecast_stats',
    'forecast_ensembles',
    'forecast_records',
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
            y=df['flow_median'],
            name='Streamflow (Median)',
            line=dict(color='black'),
        ),
        go.Scatter(
            name='Uncertainty Bounds',
            x=np.concatenate([df.index.values, df.index.values[::-1]]),
            y=np.concatenate([df['flow_uncertainty_upper'], df['flow_uncertainty_lower'][::-1]]),
            legendgroup='uncertainty',
            showlegend=True,
            fill='toself',
            line=dict(color='lightblue', dash=None)
        ),
        go.Scatter(
            name='Uncertainty Upper Bounds (80%)',
            x=df.index,
            y=df['flow_uncertainty_upper'],
            legendgroup='uncertainty',
            showlegend=False,
            line=dict(color='lightblue', dash='dash')
        ),
        go.Scatter(
            name='Uncertainty Lower Bounds (20%)',
            x=df.index,
            y=df['flow_uncertainty_lower'],
            legendgroup='uncertainty',
            showlegend=False,
            line=dict(color='lightblue', dash='dash')
        ),
    ]

    if rp_df is not None:
        rperiod_scatters = _rperiod_scatters(df.index[0], df.index[-1], rp_df, df['flow_uncertainty_upper'].max())
        scatter_traces += rperiod_scatters

    layout = go.Layout(
        title=build_title('Forecasted Streamflow', plot_titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date (UTC +0:00)', 'range': [df.index[0], df.index[-1]]},
    )

    return go.Figure(scatter_traces, layout=layout)


def forecast_stats(df: pd.DataFrame, *,
                   rp_df: pd.DataFrame = None,
                   plot_titles: list = None,
                   show_maxmin: bool = False, ) -> go.Figure:
    """
    Makes the streamflow data and optional metadata into a plotly plot

    Args:
        df: the csv response from forecast_stats
        rp_df: the csv response from return_periods
        plot_titles: a list of strings to place in the figure title. each list item will be on a new line.
        show_maxmin: Choose to show or hide the max/min envelope by default

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    # Start processing the inputs
    dates = df.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'x_stats': df['flow_avg'].dropna(axis=0).index.tolist(),
        'x_hires': df['high_res'].dropna(axis=0).index.tolist(),
        'y_max': max(df['flow_max']),
        'flow_max': list(df['flow_max'].dropna(axis=0)),
        'flow_75%': list(df['flow_75p'].dropna(axis=0)),
        'flow_avg': list(df['flow_avg'].dropna(axis=0)),
        'flow_med': list(df['flow_med'].dropna(axis=0)),
        'flow_25%': list(df['flow_25p'].dropna(axis=0)),
        'flow_min': list(df['flow_min'].dropna(axis=0)),
        'high_res': list(df['high_res'].dropna(axis=0)),
    }

    maxmin_visible = True if show_maxmin else 'legendonly'
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
        title=build_title('Forecasted Streamflow', plot_titles),
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


def forecast_ensembles(df: pd.DataFrame, *, rp_df: pd.DataFrame = None, plot_titles: list = None, ) -> go.Figure:
    """
    Makes the streamflow ensemble data and metadata into a plotly plot

    Args:
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
        'x_1-51': df['ensemble_01'].dropna(axis=0).index.tolist(),
        'x_52': df['ensemble_52'].dropna(axis=0).index.tolist(),
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
        y=plot_data['ensemble_52'],
        line=dict(color='black')
    ))
    # create a line for the rest of the ensembles (1-51)
    for i in range(1, 52):
        scatter_plots.append(go.Scatter(
            name='Ensemble ' + str(i),
            x=plot_data['x_1-51'],
            y=plot_data[f'ensemble_{i:02}'],
            legendgroup='Ensemble Members'
        ))
    scatter_plots += rperiod_scatters

    # define a layout for the plot
    layout = go.Layout(
        title=build_title('Ensemble Predicted Streamflow', plot_titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={
            'title': 'Date (UTC +0:00)',
            'range': [startdate, enddate],
            'hoverformat': '%b %d %Y',
            'tickformat': '%b %d %Y'
        },
    )
    return go.Figure(scatter_plots, layout=layout)


def forecast_records(recs: pd.DataFrame, *, rp_df: pd.DataFrame = None, plot_titles: list = False, ) -> go.Figure:
    """
    Makes the streamflow saved forecast data and metadata into a plotly plot

    Args:
        recs: the csv response from forecast_records
        rp_df: the csv response from return_periods
        plot_titles: a list of strings to place in the figure title. each list item will be on a new line.

    Return:
         plotly.GraphObject: plotly object, especially for use with python notebooks and the .show() method
    """
    # Start processing the inputs
    dates = recs.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]

    plot_data = {
        'x_records': dates,
        'recorded_flows': recs.dropna(axis=0).values.flatten(),
        'y_max': max(recs.values),
    }
    if rp_df is not None:
        plot_data.update(rp_df.to_dict(orient='index').items())
        rperiod_scatters = _rperiod_scatters(startdate, enddate, rp_df, plot_data['y_max'], plot_data['y_max'])
    else:
        rperiod_scatters = []

    scatter_plots = [go.Scatter(
        name='Previous Forecast Average',
        x=plot_data['x_records'],
        y=plot_data['recorded_flows'],
        line=dict(color='gold'),
    )] + rperiod_scatters

    layout = go.Layout(
        title=build_title('Previous Forecasted Streamflow', plot_titles=plot_titles),
        yaxis={'title': 'Streamflow (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Date (UTC +0:00)', 'range': [startdate, enddate]},
    )
    return go.Figure(scatter_plots, layout=layout)
