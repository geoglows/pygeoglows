import math

import hydrostats.data
import pandas as pd
import numpy as np

__all__ = ['compute_daily_average', 'compute_daily_variance', 'compute_monthly_average', 'compute_return_periods',
           'compute_anomaly', 'compute_daily_statistics', 'compute_low_return_periods']


def gumbel1(rp: int, xbar: float, std: float) -> float:
    """
    Solves the Gumbel Type 1 distribution
    Args:
        rp: return period (years)
        xbar: average of the dataset
        std: standard deviation of the dataset

    Returns:
        float: solution to gumbel distribution
    """
    return round(-math.log(-math.log(1 - (1 / rp))) * std * .7797 + xbar - (.45 * std), 3)


def compute_daily_average(hist: pd.DataFrame) -> pd.DataFrame:
    """
    Processes the historical simulation data into daily averages, the same as from the DailyAverages data service.

    Args:
        hist: the csv response from the HistoricSimulation streamflow data service

    Returns:
        pandas DataFrame with an index of "%m/%d" dates for each day of the year and a column labeled 'streamflow_m^3/s'
    """
    return hydrostats.data.daily_average(hist, rolling=True)


def compute_daily_variance(hist: pd.DataFrame) -> pd.DataFrame:
    """
    Processes the historical simulation data into daily variance -> the standard deviation for each day of the year

    Args:
        hist: the csv response from the HistoricSimulation streamflow data service (datetime index, 1 column of values)

    Returns:
        pandas DataFrame with an index of "%m/%d" dates for each day of the year and a column labeled 'std_dv'
    """
    daily_variance = hist.copy()
    daily_variance.columns = ['flow_std', ]
    daily_variance['day_of_year'] = daily_variance.index.strftime('%j')
    daily_variance['date'] = daily_variance.index.strftime('%m/%d')
    return daily_variance.groupby('day_of_year').std().join(daily_variance.groupby('day_of_year').first()[['date', ]])


def compute_daily_statistics(hist: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the statistics for a datafame given the day of year

    Args:
      hist: historical data to compute daily statistics from

    Return:
      pd.DataFrame: dataframe with average, min, 25% values, median, 75% value and max value for each day of year
    """
    streamflow_data = hist.copy()
    streamflow_data.index = streamflow_data.index.strftime('%m/%d')
    streamflow_data.index.name = 'day'
    daily_grouped = streamflow_data.groupby('day')
    return (
        daily_grouped.mean()
            .merge(daily_grouped.min(), left_index=True, right_index=True, suffixes=('_avg', '_min'))
            .merge(daily_grouped.quantile(.25), left_index=True, right_index=True)
            .merge(daily_grouped.median(), left_index=True, right_index=True, suffixes=('_25%', '_med'))
            .merge(daily_grouped.quantile(.75), left_index=True, right_index=True)
            .merge(daily_grouped.max(), left_index=True, right_index=True, suffixes=('_75%', '_max'))
    )


def compute_monthly_average(hist: pd.DataFrame) -> pd.DataFrame:
    """
    Processes the historic simulation data into monthly averages, the same as from the MonthlyAverages data service

    Args:
        hist: the csv response from the HistoricSimulation streamflow data service

    Returns:
        pandas DataFrame with an index of "%m" values for each month and a column labeled 'streamflow_m^3/s'
    """
    return hydrostats.data.monthly_average(hist)


def compute_return_periods(hist: pd.DataFrame, rps: tuple = (2, 5, 10, 25, 50, 100)) -> dict:
    """
    Solves the Gumbel Type-I distribution using the annual maximum flow from the historic simulation

    Args:
        hist: the csv response from the HistoricSimulation streamflow data service
        rps: a tuple of integer return period numbers to compute

    Returns:
        dictionary with keys labeled f'{return_period}_year' and float values
    """
    annual_max_flow_list = []
    return_periods = {}

    year_min = hist.index.min().year
    year_max = hist.index.max().year

    for y in range(year_min, year_max + 1):
        annual_max_flow_list.append(hist[hist.index.year == int(y)].max())

    annual_max_flow_list = np.array(annual_max_flow_list)
    xbar = np.mean(annual_max_flow_list)
    std = np.std(annual_max_flow_list)

    for rp in rps:
        return_periods[f'return_period_{rp}'] = gumbel1(rp, xbar, std)

    return return_periods


def compute_low_return_periods(hist: pd.DataFrame, rps: tuple = (2, 5, 10, 25, 50, 100)) -> dict:
    """
    Solves the Gumbel Type-I distribution using the annual minimum flow from the historic simulation

    Args:
        hist: the csv response from the HistoricSimulation streamflow data service
        rps: a tuple of integer return period numbers to compute

    Returns:
        dictionary with keys labeled f'{return_period}_year' and float values
    """
    annual_min_flow_list = []
    low_flows = {}

    year_min = hist.index.min().year
    year_max = hist.index.max().year

    for y in range(year_min, year_max + 1):
        annual_min_flow_list.append(hist[hist.index.year == int(y)].min())

    annual_min_flow_list = np.array(annual_min_flow_list)
    xbar = np.mean(annual_min_flow_list)
    std = np.std(annual_min_flow_list)

    for rp in rps:
        value = gumbel1(rp, xbar, std)
        value = value if value > 0 else 0
        low_flows[f'return_period_{rp}'] = value

    return low_flows


def compute_anomaly(stats: pd.DataFrame, day_avgs: pd.DataFrame, daily: bool = True) -> pd.DataFrame:
    """
    Compute the anomaly between the average forecasted flow and the daily average

    Args:
        stats: the csv response from the ForecastStats data service
        day_avgs: the csv response from the DailyAverages data service
        daily: if true, aggregate the hourly forecast to a daily average before computing the anomaly

    Returns:
        pandas DataFrame with a datetime index and a column labeled 'anomaly_m^3/s'
    """
    anomaly_df = pd.DataFrame(stats['flow_avg_m^3/s'], index=stats.index)
    anomaly_df = anomaly_df.dropna()

    if daily:
        anomaly_df = anomaly_df.resample('D').mean()

    anomaly_df['datetime'] = anomaly_df.index
    anomaly_df.index = anomaly_df.index.strftime("%m/%d")
    anomaly_df = anomaly_df.join(day_avgs, how="inner")
    anomaly_df['anomaly_m^3/s'] = anomaly_df['flow_avg_m^3/s'] - anomaly_df['streamflow_m^3/s']
    anomaly_df.index = anomaly_df['datetime']
    del anomaly_df['flow_avg_m^3/s'], anomaly_df['datetime'], anomaly_df['streamflow_m^3/s']

    return anomaly_df
