import matplotlib.pyplot as plt
import pandas as pd

from .format_tools import build_title


def forecast(df: pd.DataFrame, rp_df: pd.DataFrame = None, plot_titles: list = None) -> plt.subplots:
    """
    Plots forecasted streamflow and optional return periods using Matplotlib
    Args:
        df: the dataframe response from geoglows.data.forecast
        rp_df: optional dataframe of return period data
        plot_titles: optional list of strings to include in the figure title. each list item will be on a new line.

    Returns:
        matplotlib.figure.Figure
    """
    fig, ax = plt.subplots()

    # Streamflow (Median)
    ax.plot(df.index, df['flow_med_cms'], label='Streamflow (Median)', color='black')

    # Uncertainty Bounds
    ax.fill_between(
        df.index,
        df['flow_uncertainty_lower_cms'],
        df['flow_uncertainty_upper_cms'],
        label='Uncertainty Bounds (80%)',
        color='lightblue',
        alpha=0.5
    )

    # Uncertainty Upper Bounds (80%)
    ax.plot(df.index, df['flow_uncertainty_upper_cms'], label='Uncertainty Upper Bounds (80%)', linestyle='--',
            color='lightblue')

    # Uncertainty Lower Bounds (20%)
    ax.plot(df.index, df['flow_uncertainty_lower_cms'], label='Uncertainty Lower Bounds (20%)', linestyle='--',
            color='lightblue')

    if rp_df is not None:
        # todo
        pass

    # Set title and labels
    ax.set_title(build_title('Forecasted Streamflow', plot_titles))
    ax.set_ylabel('Streamflow (m^3/s)')
    ax.set_xlabel('Date (UTC +0:00)')

    # Display legend
    ax.legend()

    return fig, ax


def forecast_stats(df: pd.DataFrame, rp_df: pd.DataFrame = None, plot_titles: list = None) -> plt.subplots:
    """
    Plots forecasted streamflow and optional return periods using Matplotlib

    Args:
        df: the dataframe response from geoglows.data.forecast_stats
        rp_df: optional dataframe of return period data
        plot_titles: optional list of strings to include in the figure title. each list item will be on a new line.

    Returns:
        matplotlib.figure.Figure
    """
    fig, ax = plt.subplots()

    return fig


def forecast_ensembles(df: pd.DataFrame, rp_df: pd.DataFrame = None, plot_titles: list = None) -> plt.subplots:
    """
    Plots forecasted streamflow and optional return periods using Matplotlib

    Args:
        df: the dataframe response from geoglows.data.forecast_ensembles
        rp_df: optional dataframe of return period data
        plot_titles: optional list of strings to include in the figure title. each list item will be on a new line.

    Returns:
        matplotlib.figure.Figure
    """
    fig, ax = plt.subplots()

    return fig