import math

import numpy as np
import pandas as pd

__all__ = [
    'gumbel1',
    'simple_forecast',
    'forecast_stats',
    'daily_averages',
    'monthly_averages',
    'annual_averages',
    'daily_stats',
    'daily_variance',
    'daily_flow_anomaly',
    'return_periods',
    'low_return_periods'
]


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
    return round(-math.log(-math.log(1 - (1 / rp))) * std * .7797 + xbar - (.45 * std), 2)


def simple_forecast(ens: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the simple forecast from a dataframe of forecast ensembles

    Args:
        ens: a dataframe of forecast ensembles

    Returns:
        pandas DataFrame with datetime index and columns flow_uncertainty_upper, flow_median, flow_uncertainty_lower
    """
    df = (
        ens
        .drop(columns=['ensemble_52'])
        .dropna()
    )
    df = pd.DataFrame({
        f'flow_uncertainty_upper': np.nanpercentile(df.values, 80, axis=1),
        f'flow_median': np.median(df.values, axis=1),
        f'flow_uncertainty_lower': np.nanpercentile(df.values, 20, axis=1),
    }, index=df.index)
    return df


def forecast_stats(ens: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the statistics for a dataframe of forecast ensembles

    Args:
        ens: a dataframe of forecast ensembles

    Returns:
        pandas DataFrame with an index of datetime and columns min, max, mean, median, 25%, 75%
    """
    df = (
        ens
        .drop(columns=['ensemble_52'])
        .dropna()
    )
    return (
        pd
        .DataFrame(
            {
                'flow_min': df.min(axis=1),
                'flow_25p': df.quantile(.25, axis=1),
                'flow_avg': df.mean(axis=1),
                'flow_med': df.median(axis=1),
                'flow_75p': df.quantile(.75, axis=1),
                'flow_max': df.max(axis=1),
            },
            index=df.index
        )
        .merge(
            ens[['ensemble_52']]
            .rename(columns={'ensemble_52': 'high_res'}),
            left_index=True,
            right_index=True,
            how='outer'
        )
        .sort_index(ascending=True)
    )


def daily_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the daily average of a dataframe with a datetime index

    Args:
        df: a dataframe of retrospective simulation data

    Returns:
        pandas DataFrame with an index of "%m/%d" dates for each day of the year
    """
    return df.groupby(df.index.strftime('%m/%d')).mean()


def monthly_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the monthly average of a dataframe with a datetime index

    Args:
        df: a dataframe of retrospective simulation data

    Returns:
        pandas DataFrame with an index of "%m" values for each month
    """
    return df.groupby(df.index.strftime('%m')).mean()


def annual_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the annual average of a dataframe with a datetime index

    Args:
        df: a dataframe of retrospective simulation data

    Returns:
        pandas DataFrame with an index of "%Y" values for each year
    """
    # select years with >= 365 entries
    df = df.groupby(df.index.strftime('%Y')).filter(lambda x: len(x) >= 365)
    return df.groupby(df.index.strftime('%Y')).mean()


def daily_variance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the daily standard deviation of a dataframe with a datetime index

    Args:
        df: a dataframe of retrospective simulation data

    Returns:
        pandas DataFrame with an index of "%m/%d" dates for each day of the year
    """
    return df.groupby(df.index.strftime('%m/%d')).std()


def daily_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the statistics for a datafame given the day of year

    Args:
      df: historical data to compute daily statistics from

    Return:
      pd.DataFrame: dataframe with average, min, 25% values, median, 75% value and max value for each day of year
    """
    daily_grouped = df.groupby(df.index.strftime('%m/%d'))
    return (
        daily_grouped
        .mean()
        .merge(daily_grouped.min(), left_index=True, right_index=True, suffixes=('_avg', '_min'))
        .merge(daily_grouped.quantile(.25), left_index=True, right_index=True)
        .merge(daily_grouped.median(), left_index=True, right_index=True, suffixes=('_25%', '_med'))
        .merge(daily_grouped.quantile(.75), left_index=True, right_index=True)
        .merge(daily_grouped.max(), left_index=True, right_index=True, suffixes=('_75%', '_max'))
    )


def daily_flow_anomaly(stats: pd.DataFrame, day_avgs: pd.DataFrame, daily: bool = True) -> pd.DataFrame:
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


def return_periods(df: pd.DataFrame, rps: int or tuple = (2, 5, 10, 25, 50, 100)) -> dict:
    """
    Solves the Gumbel Type-I distribution using the annual maximum flow from the historic simulation

    Args:
        df: a dataframe of retrospective simulation data
        rps: an integer or iterable of integer return period numbers to compute

    Returns:
        dict with keys 'max_simulated' and 'return_period_{year}' for each year with float values to 2 decimals
    """
    annual_max_flow_list = df.groupby(df.index.strftime('%Y')).max().values
    xbar = np.mean(annual_max_flow_list)
    std = np.std(annual_max_flow_list)

    if type(rps) is int:
        rps = (rps,)

    ret_pers = {
        'max_simulated': round(np.max(annual_max_flow_list), 2)
    }
    ret_pers.update({f'return_period_{rp}': round(gumbel1(rp, xbar, std), 2) for rp in rps})
    return ret_pers


def low_return_periods(hist: pd.DataFrame, rps: tuple = (2, 5, 10, 25, 50, 100)) -> dict:
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
