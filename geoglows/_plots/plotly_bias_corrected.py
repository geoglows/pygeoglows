import hydrostats.data as hd
import pandas as pd
import plotly.graph_objects as go
import scipy.stats
from plotly.offline import plot as offline_plot

from .format_tools import build_title
from .plotly_helpers import _rperiod_scatters


__all__ = [
    'corrected_historical',
    'corrected_scatterplots',
    'corrected_day_average',
    'corrected_month_average',
    'corrected_volume_compare',
]


# BIAS CORRECTION PLOTS
def corrected_historical(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                         rperiods: pd.DataFrame = None, plot_titles: list = None,
                         plot_type: str = 'plotly') -> go.Figure or str:
    """
    Creates a plot of corrected discharge, observed discharge, and simulated discharge

    Args:
        corrected: the response from the geoglows.bias.correct_historical_simulation function\
        simulated: the csv response from historic_simulation
        observed: the dataframe of observed data. Must have a datetime index and a single column of flow values
        rperiods: the csv response from return_periods
        plot_type: either 'plotly', or 'plotly_html' (default plotly)
        plot_titles: (dict) Extra info to show on the title of the plot. For example:
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
        title=build_title("Historical Simulation Comparison", plot_titles),
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
                           plot_titles: list = None, ) -> go.Figure or str:
    """
    Creates a plot of corrected discharge, observed discharge, and simulated discharge. This function uses
    hydrostats.data.merge_data on the 3 inputs. If you have already computed these because you are doing a full
    comparison of bias correction, you can provide them to save time

    Args:
        corrected: the response from the geoglows.bias.correct_historical_simulation function
        simulated: the csv response from historic_simulation
        observed: the dataframe of observed data. Must have a datetime index and a single column of flow values
        merged_sim_obs: (optional) if you have already computed it, hydrostats.data.merge_data(simulated, observed)
        merged_cor_obs: (optional) if you have already computed it, hydrostats.data.merge_data(corrected, observed)
        plot_titles: (dict) Extra info to show on the title of the plot. For example:
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

    layout = go.Layout(title=build_title('Bias Correction Scatter Plot', plot_titles),
                       xaxis=dict(title='Simulated', ),
                       yaxis=dict(title='Observed', autorange=True),
                       showlegend=True, updatemenus=updatemenus)
    return go.Figure(data=scatter_sets, layout=layout)


def corrected_month_average(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                            merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                            plot_titles: list = None, ) -> go.Figure or str:
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
        plot_titles: (dict) Extra info to show on the title of the plot. For example:
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
        title=build_title('Monthly Average Streamflow Comparison', plot_titles=plot_titles),
        xaxis=dict(title='Month'), yaxis=dict(title='Discharge (m<sup>3</sup>/s)', autorange=True),
        showlegend=True)

    return go.Figure(data=scatters, layout=layout)


def corrected_day_average(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                          merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                          titles: dict = None, ) -> go.Figure or str:
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
        title=build_title('Daily Average Streamflow Comparison', titles),
        xaxis=dict(title='Days'), yaxis=dict(title='Discharge (m<sup>3</sup>/s)', autorange=True),
        showlegend=True)

    return go.Figure(data=scatters, layout=layout)


def corrected_volume_compare(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                             merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                             plot_titles: dict = None, ) -> go.Figure or str:
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
        plot_titles: (dict) Extra info to show on the title of the plot. For example:
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
        title=build_title('Cumulative Volume Comparison', plot_titles=plot_titles),
        xaxis=dict(title='Datetime', ), yaxis=dict(title='Volume (m<sup>3</sup>)', autorange=True),
        showlegend=True)

    return go.Figure(data=[observed_volume, simulated_volume, corrected_volume], layout=layout)
