import math
import warnings

import hydrostats as hs
import hydrostats.data as hd
import numpy as np
import pandas as pd
from scipy import interpolate

from .data import fdc as get_fdc
from .data import hydroweb_wse_transformer
from .data import sfdc

__all__ = [
    'correct_historical',
    'correct_forecast',
    'statistics_tables',
    'sfdc_bias_correction',
]


def correct_historical(simulated_data: pd.DataFrame, observed_data: pd.DataFrame) -> pd.DataFrame:
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
        to_prob = _flow_and_probability_mapper(monthly_simulated, to_probability=True)
        # filter the observations to current month
        monthly_observed = observed_data[observed_data.index.month == int(month)].dropna()
        to_flow = _flow_and_probability_mapper(monthly_observed, to_flow=True)

        dates += monthly_simulated.index.to_list()
        value = to_flow(to_prob(monthly_simulated.values))
        values += value.tolist()

    corrected = pd.DataFrame(data=values, index=dates, columns=['Corrected Simulated Streamflow'])
    return corrected.clip(lower=0).sort_index()


def sfdc_bias_correction(sim_data: pd.DataFrame, river_id: int) -> pd.DataFrame:
    """
    Corrects the bias in the simulated data for a given river_id using the SFDC method. This method is based on the
     https://github.com/rileyhales/saber-hbc repository.

    Args: river_id: int: a 9 digit integer that is a valid GEOGLOWS River ID number

    Returns: pandas DataFrame with a DateTime index and columns with Simulated flow, Bias Corrected Simulation flow.

    """
    assert isinstance(river_id, int), 'river_id must be an integer'
    sfdc_b = sfdc(river_id=river_id)
    fdc_b = get_fdc(river_id=river_id)

    # Process each month from January (1) to December (12)
    column_results = []
    for column in sim_data.columns:
        monthly_results = []
        for month in sorted(set(sim_data.index.month)):
            mon_sim_b = sim_data[sim_data.index.month == month].dropna().clip(lower=0)
            qb_original = mon_sim_b[column].values.flatten()
            scalar_fdc = sfdc_b.loc[month]
            sim_fdc_b_m = fdc_b.loc[month]

            flow_to_percent = _make_interpolator(sim_fdc_b_m.values.flatten(),
                                                 sim_fdc_b_m.index,
                                                 extrap='nearest',
                                                 fill_value=None)

            percent_to_scalar = _make_interpolator(scalar_fdc.index,
                                                   scalar_fdc.values.flatten(),
                                                   extrap='nearest',
                                                   fill_value=None)
            p_exceed = flow_to_percent(qb_original)
            scalars = percent_to_scalar(p_exceed)
            qb_adjusted = qb_original / scalars

            # Append the month's DataFrame to the results list
            monthly_results.append(pd.DataFrame({
                'datetime': mon_sim_b.index,
                f'{column}': qb_adjusted
            }).set_index('datetime'))
        column_results.append(pd.concat(monthly_results).sort_index())
    return pd.concat(column_results, axis=1)


def _make_interpolator(x: np.array, y: np.array, extrap: str = 'nearest',
                       fill_value: int or float = None) -> interpolate.interp1d:
    """
    Make an interpolator from two arrays

    Args:
        x: x values
        y: y values
        extrap: method for extrapolation: nearest, const, linear, average, max, min
        fill_value: value to use when extrap='const'

    Returns:
        interpolate.interp1d
    """
    # todo check that flows are not negative and have sufficient variance - even for small variance in SAF
    # if np.max(y) - np.min(y) < 5:
    #     logger.warning('The y data has similar max/min values. You may get unanticipated results.')

    # make interpolator which converts the percentiles to scalars
    if extrap == 'nearest':
        return interpolate.interp1d(x, y, fill_value='extrapolate', kind='nearest')
    elif extrap == 'const':
        if fill_value is None:
            raise ValueError('Must provide the const kwarg when extrap_method="const"')
        return interpolate.interp1d(x, y, fill_value=fill_value, bounds_error=False)
    elif extrap == 'linear':
        return interpolate.interp1d(x, y, fill_value='extrapolate')
    elif extrap == 'average':
        return interpolate.interp1d(x, y, fill_value=np.mean(y), bounds_error=False)
    elif extrap == 'max' or extrap == 'maximum':
        return interpolate.interp1d(x, y, fill_value=np.max(y), bounds_error=False)
    elif extrap == 'min' or extrap == 'minimum':
        return interpolate.interp1d(x, y, fill_value=np.min(y), bounds_error=False)
    else:
        raise ValueError('Invalid extrapolation method provided')


def correct_forecast(forecast_data: pd.DataFrame, simulated_data: pd.DataFrame,
                     observed_data: pd.DataFrame, use_month: int = 0) -> pd.DataFrame:
    """
    Accepts a short term forecast of streamflow, simulated historical flow, and observed flow timeseries and attempts
    to correct biases in the forecasted data

    Args:
        forecast_data: A dataframe with a datetime index and any number of columns of forecasted flow. Compatible with
            forecast_stats, forecast_ensembles, forecast_records
        simulated_data: A dataframe with a datetime index and a single column of streamflow values
        observed_data: A dataframe with a datetime index and a single column of streamflow values
        use_month: Optional: either 0 for correct the forecast based on the first month of the forecast data or -1 if
            you want to correct based on the ending month of the forecast data

    Returns:
        pandas DataFrame with a copy of forecasted data with values updated in each column
    """
    # make a copy of the forecasts which we update and return so the original data is not changed
    forecast_copy = forecast_data.copy()

    # make the flow and probability interpolation functions
    monthly_simulated = simulated_data[simulated_data.index.month == forecast_copy.index[use_month].month].dropna()
    monthly_observed = observed_data[observed_data.index.month == forecast_copy.index[use_month].month].dropna()
    to_prob = _flow_and_probability_mapper(monthly_simulated, to_probability=True, extrapolate=True)
    to_flow = _flow_and_probability_mapper(monthly_observed, to_flow=True, extrapolate=True)

    # for each column of forecast data, make the interpolation function and update the dataframe
    for column in forecast_copy.columns:
        tmp = forecast_copy[column].dropna()
        forecast_copy.update(pd.DataFrame(to_flow(to_prob(tmp.values)), index=tmp.index, columns=[column]))

    return forecast_copy.clip(lower=0).sort_index()


def statistics_tables(corrected: pd.DataFrame, simulated: pd.DataFrame, observed: pd.DataFrame,
                      merged_sim_obs: pd.DataFrame = False, merged_cor_obs: pd.DataFrame = False,
                      metrics: list = None) -> str:
    """
    Makes an html table of various statistical metrics for corrected vs observed data alongside the same metrics for
    the simulated vs observed data as a way to see the improvement made by the bias correction. This function uses
    hydrostats.data.merge_data on the 3 inputs. If you have already computed these because you are doing a full
    comparison of bias correction, you can provide them to save time

    Args:
        corrected: A dataframe with a datetime index and a single column of streamflow values
        simulated: A dataframe with a datetime index and a single column of streamflow values
        observed: A dataframe with a datetime index and a single column of streamflow values
        merged_sim_obs: (optional) if you have already computed it, hydrostats.data.merge_data(simulated, observed)
        merged_cor_obs: (optional) if you have already computed it, hydrostats.data.merge_data(corrected, observed)
        metrics: A list of abbreviated statistic names. See the documentation for HydroErr
    """
    if corrected is False and simulated is False and observed is False:
        if merged_sim_obs is not False and merged_cor_obs is not False:
            pass  # if you provided the merged dataframes already, we use those
    else:
        # merge the datasets together
        merged_sim_obs = hd.merge_data(sim_df=simulated, obs_df=observed)
        merged_cor_obs = hd.merge_data(sim_df=corrected, obs_df=observed)

    if metrics is None:
        metrics = ['ME', 'RMSE', 'NRMSE (Mean)', 'MAPE', 'NSE', 'KGE (2009)', 'KGE (2012)']
    # Merge Data
    table1 = hs.make_table(merged_dataframe=merged_sim_obs, metrics=metrics)
    table2 = hs.make_table(merged_dataframe=merged_cor_obs, metrics=metrics)

    table2 = table2.rename(index={'Full Time Series': 'Corrected Full Time Series'})
    table1 = table1.rename(index={'Full Time Series': 'Original Full Time Series'})
    table1 = table1.transpose()
    table2 = table2.transpose()

    table_final = pd.merge(table1, table2, right_index=True, left_index=True)

    return table_final.to_html()


def _flow_and_probability_mapper(monthly_data: pd.DataFrame, to_probability: bool = False,
                                 to_flow: bool = False, extrapolate: bool = False) -> interpolate.interp1d:
    if not to_flow and not to_probability:
        raise ValueError('You need to specify either to_probability or to_flow as True')
    if to_flow and to_probability:
        raise ValueError('You cannot specify both to_probability and to_flow as True')

    # get maximum value to bound histogram
    max_val = math.ceil(np.max(monthly_data.max()))
    min_val = math.floor(np.min(monthly_data.min()))

    if max_val == min_val:
        warnings.warn('The observed data have the same max and min value. You may get unanticipated results.')
        max_val += .1

    # determine number of histograms bins needed
    number_of_points = len(monthly_data.values)
    number_of_classes = math.ceil(1 + (3.322 * math.log10(number_of_points)))

    # specify the bin width for histogram (in m3/s)
    step_width = (max_val - min_val) / number_of_classes

    # specify histogram bins
    bins = np.arange(-np.min(step_width), max_val + 2 * np.min(step_width), np.min(step_width))

    if bins[0] == 0:
        bins = np.concatenate((-bins[1], bins))
    elif bins[0] > 0:
        bins = np.concatenate((-bins[0], bins))

    # make the histogram
    counts, bin_edges = np.histogram(monthly_data, bins=bins)

    # adjust the bins to be the center
    bin_edges = bin_edges[1:]

    # normalize the histograms
    counts = counts.astype(float) / monthly_data.size

    # calculate the cdfs
    cdf = np.cumsum(counts)

    # interpolated function to convert simulated streamflow to prob
    if to_probability:
        if extrapolate:
            return interpolate.interp1d(bin_edges, cdf, fill_value='extrapolate')
        else:
            return interpolate.interp1d(bin_edges, cdf)
    # interpolated function to convert simulated prob to observed streamflow
    elif to_flow:
        if extrapolate:
            return interpolate.interp1d(cdf, bin_edges, fill_value='extrapolate')
        return interpolate.interp1d(cdf, bin_edges)


def transform_forecast_to_hydroweb_wse(df: pd.DataFrame, river_id: int):
    """
    Transforms the streamflow data to water surface elevation using the SFDC table

    Args:
        df: a dataframe of streamflow data with a datetime index
        river_id: an integer of the river_id

    Returns:
        pandas DataFrame with water surface elevation values
    """
    hwt = hydroweb_wse_transformer(river_id=river_id)
    fdc = get_fdc(river_id=river_id, resolution='hourly', kind='monthly')  # hourly because its for forecast only

    wse = []
    for month in df.index.month.unique():
        wse_columns = {}
        for column in df.columns:
            prob = np.interp(
                df[df.index.month == month][column].values.flatten(),
                fdc.loc[month].values.flatten(),
                fdc.loc[month].index.values.flatten()
            )
            wse_columns[column] = np.interp(
                prob,
                hwt.loc[month].index.values.flatten(),
                hwt.loc[month].values.flatten()
            )
        wse.append(pd.DataFrame(wse_columns, index=df[df.index.month == month].index))
    wse = pd.concat(wse, axis=0).sort_index()
    return wse
