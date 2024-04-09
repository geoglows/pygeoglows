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
    annual_averages as plotly_annual_averages
)


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
    # elif plot_type == 'matplotlib':
    #     return mpl_forecast(df, rp_df=rp_df, plot_titles=plot_titles)
    else:
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
    # elif plot_type in ('matplotlib', 'mpl'):
    #     return mpl_forecast_stats(df, rp_df=rp_df, plot_titles=plot_titles)
    else:
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
    # elif plot_type == 'matplotlib':
    #     return mpl_forecast_ensembles(df, rp_df=rp_df, plot_titles=plot_titles)
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def retrospective(df: pd.DataFrame, *,
                  plot_type: str = 'plotly',
                  rp_df: pd.DataFrame = None,
                  plot_titles: list = None, ) -> go.Figure:
    if plot_type in ('plotly', 'html'):
        figure = plotly_retrospective(df, rp_df=rp_df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    # if plot_type == 'matplotlib':
    #     return mpl_retrospective(df, rp_df=rp_df, plot_titles=plot_titles)
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def daily_averages(df: pd.DataFrame, *,
                   plot_type: str = 'plotly',
                   plot_titles: list = None, ) -> go.Figure:
    if plot_type in ('plotly', 'html'):
        figure = plotly_daily_averages(df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    # if plot_type == 'matplotlib':
    #     return mpl_daily_averages(df, plot_titles=plot_titles)
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def monthly_averages(df: pd.DataFrame, *,
                     plot_type: str = 'plotly',
                     plot_titles: list = None, ) -> go.Figure:
    if plot_type in ('plotly', 'html'):
        figure = plotly_monthly_averages(df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    # if plot_type == 'matplotlib':
    #     return mpl_monthly_averages(df, plot_titles=plot_titles)
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def annual_averages(df: pd.DataFrame, *,
                    plot_type: str = 'plotly',
                    plot_titles: list = None, ) -> go.Figure:
    if plot_type in ('plotly', 'html'):
        figure = plotly_annual_averages(df, plot_titles=plot_titles)
        if plot_type == 'html':
            return plotly_figure_to_html_plot(figure)
        return figure
    # if plot_type == 'matplotlib':
    #     return mpl_annual_averages(df, plot_titles=plot_titles)
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def daily_variance(df: pd.DataFrame, *,
                   plot_type: str = 'plotly',
                   plot_titles: list = None, ) -> go.Figure:
    if plot_type == 'plotly':
        return
    # if plot_type == 'matplotlib':
    #     return
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')


def flow_duration_curve(df: pd.DataFrame, *,
                        plot_type: str = 'plotly',
                        plot_titles: list = None, ) -> go.Figure:
    if plot_type == 'plotly':
        return
    # if plot_type == 'matplotlib':
    #     return
    else:
        raise NotImplementedError(f'Plot type "{plot_type}" is not supported.')
