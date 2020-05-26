import math
from functools import reduce

import numpy as np
import pandas as pd
from scipy import interpolate

__all__ = ['correct_historical_simulation']


def correct_historical_simulation(simulated_data: pd.DataFrame, observed_data: pd.DataFrame) -> pd.DataFrame:
    """
    Accepts a historically simulated flow timeseries and observed flow timeseries and attempts to correct biases in the
    simulation on a monthly basis.

    Args:
        simulated_data: A dataframe with a datetime index and a single column of streamflow values
        observed_data: A dataframe with a datetime index and a single column of streamflow values

    Returns:
        pandas DataFrame with a datetime index and a single column of streamflow values
    """
    # list of the unique months in the historical simulation. should always be 1->12 but just in case...
    unique_simulation_months = sorted(set(simulated_data.index.strftime('%m')))
    dates = []
    values = []

    for month in unique_simulation_months:

        # filter historic data to only be current month
        monthly_simulated = simulated_data[simulated_data.index.month == int(month)].dropna()
        # filter the observations to current month
        monthly_observed = observed_data[observed_data.index.month == int(month)].dropna()

        # get maximum value to bound histogram
        obs_maxVal = math.ceil(np.max(monthly_observed.max()))
        sim_maxVal = math.ceil(np.max(monthly_simulated.max()))
        obs_minVal = math.floor(np.min(monthly_observed.min()))
        sim_minVal = math.floor(np.min(monthly_simulated.min()))

        n_elementos_obs = len(monthly_observed.values)
        n_elementos_sim = len(monthly_simulated.values)

        n_marcas_clase_obs = math.ceil(1 + (3.322 * math.log10(n_elementos_obs)))
        n_marcas_clase_sim = math.ceil(1 + (3.322 * math.log10(n_elementos_sim)))

        # specify the bin width for histogram (in m3/s)
        step_obs = (obs_maxVal - obs_minVal) / n_marcas_clase_obs
        step_sim = (sim_maxVal - sim_minVal) / n_marcas_clase_sim

        # specify histogram bins
        bins_obs = np.arange(-np.min(step_obs), obs_maxVal + 2 * np.min(step_obs), np.min(step_obs))
        bins_sim = np.arange(-np.min(step_sim), sim_maxVal + 2 * np.min(step_sim), np.min(step_sim))

        if bins_obs[0] == 0:
            bins_obs = np.concatenate((-bins_obs[1], bins_obs))
        elif bins_obs[0] > 0:
            bins_obs = np.concatenate((-bins_obs[0], bins_obs))

        if bins_sim[0] >= 0:
            bins_sim = np.concatenate((-bins_sim[1], bins_sim))
        elif bins_sim[0] > 0:
            bins_sim = np.concatenate((-bins_sim[0], bins_sim))

        # get the histograms
        sim_counts, bin_edges_sim = np.histogram(monthly_simulated, bins=bins_sim)
        obs_counts, bin_edges_obs = np.histogram(monthly_observed, bins=bins_obs)

        # adjust the bins to be the center
        bin_edges_sim = bin_edges_sim[1:]
        bin_edges_obs = bin_edges_obs[1:]

        # normalize the histograms
        sim_counts = sim_counts.astype(float) / monthly_simulated.size
        obs_counts = obs_counts.astype(float) / monthly_observed.size

        # calculate the cdfs
        simcdf = np.cumsum(sim_counts)
        obscdf = np.cumsum(obs_counts)

        # interpolated function to convert simulated streamflow to prob
        f = interpolate.interp1d(bin_edges_sim, simcdf)

        # interpolated function to convert simulated prob to observed streamflow
        backout = interpolate.interp1d(obscdf, bin_edges_obs)

        date = monthly_simulated.index.to_list()
        value = backout(f(monthly_simulated.values))
        value = value.tolist()

        dates.append(date)
        values.append(value)

    dates = reduce(lambda x, y: x + y, dates)
    values = reduce(lambda x, y: x + y, values)

    corrected = pd.DataFrame(data=values, index=dates, columns=['Corrected Simulated Streamflow'])
    corrected.sort_index(inplace=True)
    return corrected
