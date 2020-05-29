import pandas as pd

import geoglows


def get_forecast_data_with_reach_id_region(reach_id, region, endpoint=geoglows.streamflow.ENDPOINT):
    stats = geoglows.streamflow.forecast_stats(reach_id, endpoint=endpoint)
    ensembles = geoglows.streamflow.forecast_ensembles(reach_id, endpoint=endpoint)
    warnings = geoglows.streamflow.forecast_warnings(region, endpoint=endpoint)
    records = geoglows.streamflow.forecast_records(reach_id, endpoint=endpoint)
    return stats, ensembles, warnings, records


def get_historical_data_with_reach_id(reach_id, endpoint=geoglows.streamflow.ENDPOINT, forcing='era_5'):
    historical = geoglows.streamflow.historic_simulation(reach_id, forcing, endpoint=endpoint)
    seasonal = geoglows.streamflow.seasonal_average(reach_id, forcing, endpoint=endpoint)
    rperiods = geoglows.streamflow.return_periods(reach_id, forcing, endpoint=endpoint)
    return historical, seasonal, rperiods


def request_all_data_with_lat_lon(lat, lon):
    stats = geoglows.streamflow.forecast_stats(False, lat=lat, lon=lon)
    ensembles = geoglows.streamflow.forecast_ensembles(False, lat=lat, lon=lon)
    warnings = geoglows.streamflow.forecast_warnings(region)
    records = geoglows.streamflow.forecast_records(False, lat=lat, lon=lon)
    historical = geoglows.streamflow.historic_simulation(False, lat=lat, lon=lon)
    seasonal = geoglows.streamflow.seasonal_average(False, lat=lat, lon=lon)
    rperiods = geoglows.streamflow.return_periods(False, lat=lat, lon=lon)
    return stats, ensembles, warnings, records, historical, seasonal, rperiods


def plot_all(stats, ensembles, warnings, records, historical, seasonal, rperiods=None):
    geoglows.plots.hydroviewer(records, stats, ensembles, rperiods).show()
    geoglows.plots.forecast_stats(stats, rperiods).show()
    geoglows.plots.forecast_ensembles(ensembles, rperiods).show()
    geoglows.plots.forecast_records(records, rperiods).show()
    geoglows.plots.historic_simulation(historical, rperiods).show()
    geoglows.plots.seasonal_average(seasonal).show()
    geoglows.plots.flow_duration_curve(historical).show()

    # with open('/Users/riley/spatialdata/prob_table.html', 'w') as f:
    #     f.write(geoglows.streamflow.probabilities_table(stats, ensembles, rperiods))
    # with open('/Users/riley/spatialdata/rper_table.html', 'w') as f:
    #     f.write(geoglows.streamflow.return_periods_table(rperiods))

    print(warnings.head(10))

    return


def test_bias_correction():
    station = 23097040
    comid = 9007292
    stats = geoglows.streamflow.forecast_stats(comid)
    ens = geoglows.streamflow.forecast_ensembles(comid)
    records = geoglows.streamflow.forecast_records(comid)
    hist = geoglows.streamflow.historic_simulation(comid)
    observed_df = pd.read_csv('/Users/rileyhales/Downloads/23187280.csv', index_col=0)
    observed_df.index = pd.to_datetime(observed_df.index).tz_localize('UTC')
    observed_df.index.name = 'datetime'
    corrected = geoglows.bias.correct_historical_sim(hist, observed_df)
    cor_stats = geoglows.bias.correct_forecast(stats, hist, observed_df)
    cor_ens = geoglows.bias.correct_forecast(ens, hist, observed_df)
    cor_recr = geoglows.bias.correct_forecast(records, hist, observed_df, use_month=-1)
    geoglows.plots.hydroviewer(cor_recr, cor_stats, cor_ens).show()
    geoglows.plots.corrected_scatterplots(corrected, hist, observed_df).show()
    geoglows.plots.corrected_day_average(corrected, hist, observed_df).show()
    geoglows.plots.corrected_month_average(corrected, hist, observed_df).show()
    geoglows.plots.corrected_volume_compare(corrected, hist, observed_df).show()
    html = geoglows.bias.make_statistics_tables(corrected, hist, observed_df)
    with open('/Users/riley/spatialdata/testtable.html', 'w') as f:
        f.write(html)
    return


if __name__ == '__main__':
    test_bias_correction()
