import math
import warnings

import hydrostats as hs
import hydrostats.data as hd
import numpy as np
import pandas as pd
from scipy import interpolate
from scipy import stats
from .data import retrieve_sfdc_for_river_id, retrieve_fdc
from .data import retrospective

__all__ = [
    'correct_historical',
    'correct_forecast',
    'statistics_tables',
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
    corrected.sort_index(inplace=True)
    return corrected

def do_bias_correction_for_me(river_id: int) -> pd.DataFrame:
    """
    Corrects the bias in the simulated data for a given river_id using the SFDC method. This method is based on the
     https://github.com/rileyhales/saber-hbc repository.

    Args: river_id: int: a 9 digit integer that is a valid GEOGLOWS River ID number

    Returns: pandas DataFrame with a DateTime index and columns with Simulated flow, Bias Corrected Simulation flow.

    """
    simulated_data = retrospective(river_id=river_id)
    sfdc_b = retrieve_sfdc_for_river_id(river_id=river_id) # I used to provide  sfdc_table_path and saber_assign_table_path in the arguments in my local environment
    sim_fdc_b = retrieve_fdc(river_id=river_id) # I used to provide fdc_table_path in the arguments in my local environment
    # List to store results for each month
    monthly_results = []

    # Process each month from January (1) to December (12)
    for month in sorted(set(simulated_data.index.month)):
        mon_sim_b = simulated_data[simulated_data.index.month == month].dropna().clip(lower=0)

        qb_original = mon_sim_b['Qout'].values.flatten() #'Qout maynot be the column header
        scalar_fdc = sfdc_b[sfdc_b['month'] == month][['p_exceed', 'sfdc']].set_index('p_exceed')
        sim_fdc_b_m = sim_fdc_b[sim_fdc_b['month'] == month][['p_exceed', 'fdc']].set_index('p_exceed')

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

        # Create a DataFrame for this month's results
        month_df = pd.DataFrame({
            'date': mon_sim_b.index,
            'Simulated': qb_original,
            'Bias Corrected Simulation': qb_adjusted
        })

        # Append the month's DataFrame to the results list
        monthly_results.append(month_df)
    return pd.concat(monthly_results).set_index('date').sort_index()

def bias_correct_ungauge(simulated_data: pd.DataFrame, sfdc: pd.DataFrame) -> pd.DataFrame:
    """
    Perform bias correction on the simulated data using the SFDC table.

    Args:
        simulated_data (pd.DataFrame): DataFrame containing the simulated data to be bias-corrected.
        sfdc (pd.DataFrame): DataFrame containing the SFDC table for the corresponding river.

    Returns:
        pd.DataFrame: DataFrame with bias-corrected simulated data.
    """
    # List to store results for each month
    monthly_results = []

    # Process each month from January (1) to December (12)
    for month in sorted(set(simulated_data.index.month)):
        mon_sim = simulated_data[simulated_data.index.month == month].dropna().clip(lower=0)

        qb_original = mon_sim['Qout'].values.flatten()
        scalar_fdc = sfdc[sfdc['month'] == month][['p_exceed', 'sfdc']].set_index('p_exceed')
        flow_to_percent = _make_interpolator(scalar_fdc['sfdc'].values.flatten(),
                                             scalar_fdc.index,
                                             extrap='nearest',
                                             fill_value=None)
        p_exceed = flow_to_percent(qb_original)
        percent_to_scalar = _make_interpolator(scalar_fdc.index,
                                               scalar_fdc['sfdc'].values.flatten(),
                                               extrap='nearest',
                                               fill_value=None)
        scalars = percent_to_scalar(p_exceed)
        qb_adjusted = qb_original / scalars

        # Create a DataFrame for this month's results
        month_df = pd.DataFrame({
            'date': mon_sim.index,
            'Simulated': qb_original,
            'Bias Corrected Simulation': qb_adjusted
        })

        # Append the month's DataFrame to the results list
        monthly_results.append(month_df)

    return pd.concat(monthly_results).set_index('date').sort_index()




def make_sfdc(simulated_df: pd.DataFrame, gauge_df: pd.DataFrame,
              use_log: bool = False,fix_seasonally: bool = True, empty_months: str = 'skip',
              drop_outliers: bool = False, outlier_threshold: int or float = 2.5,
              filter_scalar_fdc: bool = False, filter_range: tuple = (0, 80),
              extrapolate: str = 'nearest', fill_value: int or float = None,
              fit_gumbel: bool = False, fit_range: tuple = (10, 90),
              metadata: bool = False, ) -> pd.DataFrame:
    """
    Makes a scalar flow duration curve (SFDC) mapping from simulated to observed (gauge) flow data. SFDC is used in SABER to
    correct timeseries data for a ungauged riverid.

    Args:
        simulated_data: A dataframe with a datetime index and a single column of simulated streamflow values
        gauge_df: A dataframe with a datetime index and a single column of observed streamflow values
        extrapolate: Method to use for extrapolation. Options: nearest, const, linear, average, max, min
        fill_value: Value to use for extrapolation when extrapolate_method='const'
        filter_range: Lower and upper bounds of the filter range
        drop_outliers: Flag to exclude outliers
        outlier_threshold: Number of std deviations from mean to exclude from flow duration curve

    Returns:
        pandas DataFrame with a DateTime index and columns with corrected flow, uncorrected flow, the scalar adjustment
        factor applied to correct the discharge, and the percentile of the uncorrected flow (in the seasonal grouping,
        if applicable).
    """
    if fix_seasonally:
        # list of the unique months in the historical simulation. should always be 1->12 but just in case...
        monthly_results = []
        for month in sorted(set(simulated_df.index.strftime('%m'))):
            # filter data to current iteration's month
            mon_obs_a = gauge_df[gauge_df.index.month == int(month)].dropna().clip(lower=0)
            if mon_obs_a.empty:
                if empty_months == 'skip':
                    continue
                else:
                    raise ValueError(f'Invalid value for argument "empty_months". Given: {empty_months}.')

            mon_sim_b = simulated_df[simulated_df.index.month == int(month)].dropna().clip(lower=0)
            monthly_results.append(make_sfdc(
                mon_obs_a, mon_sim_b,
                fix_seasonally=False, empty_months=empty_months,
                drop_outliers=drop_outliers, outlier_threshold=outlier_threshold,
                filter_scalar_fdc=filter_scalar_fdc, filter_range=filter_range,
                extrapolate=extrapolate, fill_value=fill_value,
                fit_gumbel=fit_gumbel, fit_range=fit_range, )
            )
        # combine the results from each monthly into a single dataframe (sorted chronologically) and return it
        return pd.concat(monthly_results).sort_index()


    if drop_outliers:
        simulated_df = _drop_outliers_by_zscore(simulated_df, threshold=outlier_threshold)
        gauge_df = _drop_outliers_by_zscore(gauge_df, threshold=outlier_threshold)

    # compute the flow duration curves
    sim_fdc = fdc(simulated_df)
    obs_fdc = fdc(gauge_df)

    # calculate the scalar flow duration curve
    scalar_fdc = sfdc(sim_fdc, obs_fdc)

    return scalar_fdc

def fdc(flows: np.array, steps: int = 101, col_name: str = 'Q') -> pd.DataFrame:
    """
    Compute flow duration curve (exceedance probabilities) from a list of flows

    Args:
        flows: array of flows
        steps: number of steps (exceedance probabilities) to use in the FDC
        col_name: name of the column in the returned dataframe

    Returns:
        pd.DataFrame with index 'p_exceed' and columns 'Q' (or col_name)
    """
    # calculate the FDC and save to parquet
    exceed_prob = np.linspace(100, 0, steps)
    fdc_flows = np.nanpercentile(flows, exceed_prob)
    df = pd.DataFrame(fdc_flows, columns=[col_name, ], index=exceed_prob)
    df.index.name = 'p_exceed'
    return df

def _drop_outliers_by_zscore(df: pd.DataFrame, threshold: float = 3) -> pd.DataFrame:
    """
    Drop outliers from a dataframe by their z-score and a threshold
    Based on https://stackoverflow.com/questions/23199796/detect-and-exclude-outliers-in-pandas-data-frame
    Args:
        df: dataframe to drop outliers from
        threshold: z-score threshold

    Returns:
        pd.DataFrame with outliers removed
    """
    return df[(np.abs(stats.zscore(df)) < threshold).all(axis=1)]

def sfdc(sim_fdc: pd.DataFrame, obs_fdc: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the scalar flow duration curve (exceedance probabilities) from two flow duration curves

    Args:
        sim_fdc: simulated flow duration curve
        obs_fdc: observed flow duration curve

    Returns:
        pd.DataFrame with index (exceedance probabilities) and a column of scalars
    """
    scalars_df = pd.DataFrame(np.divide(sim_fdc.values.flatten(),obs_fdc.values.flatten()),
        columns=['scalars', ],
        index=sim_fdc.index
    )
    scalars_df.replace(np.inf, np.nan, inplace=True)
    scalars_df.dropna(inplace=True)
    return scalars_df

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

    return forecast_copy


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

    # get maximum value to bound histogram
    max_val = math.ceil(np.max(monthly_data.max()))
    min_val = math.floor(np.min(monthly_data.min()))

    if max_val == min_val:
        warnings.warn('The observational data has the same max and min value. You may get unanticipated results.')
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
            func = interpolate.interp1d(bin_edges, cdf, fill_value='extrapolate')
        else:
            func = interpolate.interp1d(bin_edges, cdf)
        return lambda x: np.clip(func(x), 0, 1)
    # interpolated function to convert simulated prob to observed streamflow
    elif to_flow:
        if extrapolate:
            return interpolate.interp1d(cdf, bin_edges, fill_value='extrapolate')
        return interpolate.interp1d(cdf, bin_edges)
