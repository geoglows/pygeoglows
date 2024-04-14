import pandas as pd
import plotly.graph_objects as go

from .format_tools import plotly_figure_to_html_plot
from .plotly_forecasts import (
    forecast as plotly_forecast,
    forecast_stats as plotly_forecast_stats,
    forecast_ensembles as plotly_forecast_ensembles
)
from .plotly_retrospective import (
    retrospective as plotly_retrospective,
    daily_averages as plotly_daily_averages,
    monthly_averages as plotly_monthly_averages,
    annual_averages as plotly_annual_averages,
    flow_duration_curve as plotly_flow_duration_curve,
)
from .plotly_bias_corrected import (
    corrected_retrospective as plotly_corrected_retrospective,
    corrected_month_average as plotly_corrected_month_average,
    corrected_day_average as plotly_corrected_day_average,
    corrected_scatterplots as plotly_corrected_scatterplots,
)

__all__ = [
    'forecast',
    'forecast_stats',
    'forecast_ensembles',

    'retrospective',
    'daily_averages',
    'monthly_averages',
    'annual_averages',
    'flow_duration_curve',

    'corrected_retrospective',
    'corrected_month_average',
    'corrected_day_average',
    'corrected_scatterplots',
]


def forecast(df: pd.DataFrame, *,
             plot_type: str = 'plotly',
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
    if plot_type in ('plotly', 'html'):
        figure = plotly_forecast(df, rp_df=rp_df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def forecast_stats(df: pd.DataFrame, *,
                   plot_type: str = 'plotly',
                   rp_df: pd.DataFrame = None,
                   plot_titles: list = None, ) -> go.Figure:
    """
    Plots forecasted streamflow and optional return periods
    Args:
         df: the dataframe response from geoglows.data.forecast_stats
         rp_df: optional dataframe of return period data
         plot_titles: optional list of strings to include in the figure title. each list item will be on a new line.

    Returns:
         go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_forecast_stats(df, rp_df=rp_df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def forecast_ensembles(df: pd.DataFrame, *,
                       plot_type: str = 'plotly',
                       rp_df: pd.DataFrame = None,
                       plot_titles: list = None, ) -> go.Figure:
    """
    Plots forecasted streamflow and optional return periods
    Args:
           df: the dataframe response from geoglows.data.forecast_ensembles
           rp_df: optional dataframe of return period data
           plot_titles: optional list of strings to include in the figure title. each list item will be on a new line.

    Returns:
           go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_forecast_ensembles(df, rp_df=rp_df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def retrospective(df: pd.DataFrame, *,
                  plot_type: str = 'plotly',
                  rp_df: pd.DataFrame = None,
                  plot_titles: list = None, ) -> go.Figure:
    """
    Plots the retrospective simulation data

    Args:
        df: a dataframe of the retrospective simulation
        plot_type: either plotly or html
        rp_df: a dataframe with the response from the return periods dataset
        plot_titles: additional key-value pairs to display in the title of the figure

    Returns:
        go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_retrospective(df, rp_df=rp_df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def daily_averages(df: pd.DataFrame, *,
                   plot_type: str = 'plotly',
                   plot_titles: list = None, ) -> go.Figure:
    """
    Makes a plotly figure of the daily average flows

    Args:
        df: a dataframe of the daily average flows
        plot_type: either plotly or html
        plot_titles: additional key-value pairs to display in the title of the figure

    Returns:
        go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_daily_averages(df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def monthly_averages(df: pd.DataFrame, *,
                     plot_type: str = 'plotly',
                     plot_titles: list = None, ) -> go.Figure:
    """
    Makes a plotly figure of the monthly average flows

    Args:
        df: a dataframe of the monthly average flows
        plot_type: either plotly or html
        plot_titles: additional key-value pairs to display in the title of the figure

    Returns:
        go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_monthly_averages(df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def annual_averages(df: pd.DataFrame, *,
                    plot_type: str = 'plotly',
                    plot_titles: list = None, ) -> go.Figure:
    """
    Makes a plotly figure of the annual average flows

    Args:
        df: a dataframe of the annual average flows
        plot_type: either plotly or html
        plot_titles: additional key-value pairs to display in the title of the figure

    Returns:
        go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_annual_averages(df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def flow_duration_curve(df: pd.DataFrame, *,
                        plot_type: str = 'plotly',
                        plot_titles: list = None, ) -> go.Figure:
    """
    Makes a plotly figure of the flow duration curve

    Args:
        df: a dataframe of the flow duration curve values
        plot_type: either plotly or html
        plot_titles: additional key-value pairs to display in the title of the figure

    Returns:
        go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_flow_duration_curve(df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def corrected_retrospective(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                            rperiods: pd.DataFrame = None, plot_titles: list = None,
                            plot_type: str = 'plotly', ) -> go.Figure:
    """
    Makes a plotly figure of bias corrected retrospective simulation data

    Args:
        corrected: the bias corrected simulation dataframe
        simulated: the retrospective simulation dataframe
        observed: the in situ measurements used to bias correct the simulation
        rperiods: the return periods for the simulated river
        plot_type: either plotly or html
        plot_titles: additional key-value pairs to display in the title of the figure

    Returns:
        go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_corrected_retrospective(corrected, simulated, observed, rperiods, plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def corrected_month_average(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                            plot_titles: list = None, plot_type: str = 'plotly', ) -> go.Figure:
    """
    Makes a plotly figure of bias corrected monthly average simulation data

    Args:
        corrected: the bias corrected simulation dataframe
        simulated: the retrospective simulation dataframe
        observed: the in situ measurements used to bias correct the simulation
        plot_type: either plotly or html
        plot_titles: additional key-value pairs to display in the title of the figure

    Returns:
        go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_corrected_month_average(corrected, simulated, observed, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def corrected_day_average(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                          plot_titles: list = None, plot_type: str = 'plotly', ) -> go.Figure:
    """
    Makes a plotly figure of bias corrected daily average simulation data

    Args:
        corrected: the bias corrected simulation dataframe
        simulated: the retrospective simulation dataframe
        observed: the in situ measurements used to bias correct the simulation
        plot_type: either plotly or html
        plot_titles: additional key-value pairs to display in the title of the figure

    Returns:
        go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_corrected_day_average(corrected, simulated, observed, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def corrected_scatterplots(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                           plot_titles: list = None, plot_type: str = 'plotly', ) -> go.Figure:
    """
    Makes a plotly figure of scatter _plots showing the performance of the bias correction process

    Args:
        corrected: the bias corrected simulation dataframe
        simulated: the retrospective simulation dataframe
        observed: the in situ measurements used to bias correct the simulation
        plot_type: either plotly or html
        plot_titles: additional key-value pairs to display in the title of the figure

    Returns:
        go.Figure
    """
    if plot_type in ('plotly', 'html'):
        figure = plotly_corrected_scatterplots(corrected, simulated, observed, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')
