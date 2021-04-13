import pandas as pd
import hydrostats.data
import math
import statistics

__all__ = ['compute_daily_average', 'compute_monthly_average', 'compute_return_periods', 'compute_anomaly']


def compute_daily_average(hist: pd.DataFrame) -> pd.DataFrame:
    """
    Processes the historic simulation data into daily averages, the same as from the DailyAverages data service.

    Args:
        hist: the csv response from the HistoricSimulation streamflow data service

    Returns:
        pandas DataFrame with an index of "%m/%d" dates for each day of the year and a column labeled 'streamflow_m^3/s'
    """
    return hydrostats.data.daily_average(hist, rolling=True)


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

    xbar = statistics.mean(annual_max_flow_list)
    std = statistics.stdev(annual_max_flow_list)

    for rp in rps:
        return_periods[f'{rp}_year'] = -math.log(-math.log(1 - (1 / rp))) * std * .7797 + xbar - (.45 * std)

    return return_periods


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
