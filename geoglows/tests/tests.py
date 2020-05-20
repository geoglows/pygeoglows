import geoglows.streamflow as sf


def get_forecast_data_with_reach_id_region(reach_id, region, endpoint):
    stats = sf.forecast_stats(reach_id, endpoint=endpoint)
    ensembles = sf.forecast_ensembles(reach_id, endpoint=endpoint)
    warnings = sf.forecast_warnings(region, endpoint=endpoint)
    records = sf.forecast_records(reach_id, endpoint=endpoint)
    return stats, ensembles, warnings, records


def get_historical_data_with_reach_id(reach_id, endpoint, forcing='era_5'):
    historical = sf.historic_simulation(reach_id, forcing, endpoint=endpoint)
    seasonal = sf.seasonal_average(reach_id, forcing, endpoint=endpoint)
    rperiods = sf.return_periods(reach_id, forcing, endpoint=endpoint)
    return historical, seasonal, rperiods


def request_all_data_with_lat_lon(lat, lon):
    stats = sf.forecast_stats(False, lat=lat, lon=lon)
    ensembles = sf.forecast_ensembles(False, lat=lat, lon=lon)
    warnings = sf.forecast_warnings(region)
    records = sf.forecast_records(False, lat=lat, lon=lon)

    historical_int = sf.historic_simulation(False, lat=lat, lon=lon)
    historical_5 = sf.historic_simulation(False, lat=lat, lon=lon, forcing='era_5')
    seasonal_int = sf.seasonal_average(False, lat=lat, lon=lon)
    seasonal_5 = sf.seasonal_average(False, lat=lat, lon=lon, forcing='era_5')
    rperiods_int = sf.return_periods(False, lat=lat, lon=lon)
    rperiods_5 = sf.return_periods(False, lat=lat, lon=lon, forcing='era_5')

    return stats, ensembles, warnings, records, historical_int, historical_5, \
           seasonal_int, seasonal_5, rperiods_int, rperiods_5


def plot_all(stats, ensembles, warnings, records, historical, seasonal, rperiods=None):
    # does not need warnings
    plot = sf.hydroviewer_plot(records, stats, ensembles, rperiods)
    plot.show()
    plot = sf.forecast_plot(stats, rperiods)
    plot.show()
    plot = sf.ensembles_plot(ensembles, rperiods)
    plot.show()
    plot = sf.records_plot(records, rperiods)
    plot.show()
    plot = sf.records_plot(records)
    plot.show()

    plot = sf.historical_plot(historical, rperiods)
    plot.show()
    plot = sf.seasonal_plot(seasonal)
    plot.show()
    plot = sf.flow_duration_curve_plot(historical)
    plot.show()

    # with open('/Users/riley/spatialdata/tables.html', 'w') as f:
    #     f.write(sf.probabilities_table(stats, ensembles, rperiods))
    sf.probabilities_table(stats, ensembles, rperiods)
    sf.return_periods_table(rperiods)

    print(warnings.head(10))

    return


if __name__ == '__main__':
    reach_id = 3001070
    region = 'japan-geoglows'
    lat = 36.203917
    lon = 139.435292

    # stats, ensembles, warnings, records = get_forecast_data_with_reach_id_region(reach_id, region, sf.LOCAL_ENDPOINT)
    # historical, seasonal, rperiods = get_historical_data_with_reach_id(reach_id, sf.LOCAL_ENDPOINT)
    # historical, seasonal, rperiods = get_historical_data_with_reach_id(reach_id, forcing='era_interim')
    # plot_all(stats, ensembles, warnings, records, historical, seasonal, rperiods)
    # sf.hydroviewer_plot(records, stats, ensembles, rperiods).show()

    # with open('/Users/riley/spatialdata/table.html', 'w') as t:
    #     t.write(sf.probabilities_table(stats, ensembles, rperiods))
    stats = sf.forecast_stats(reach_id, endpoint=sf.LOCAL_ENDPOINT)
    ensembles = sf.forecast_ensembles(reach_id, endpoint=sf.LOCAL_ENDPOINT)
    warnings = sf.forecast_warnings(region, endpoint=sf.LOCAL_ENDPOINT)
    records = sf.forecast_records(reach_id, endpoint=sf.LOCAL_ENDPOINT)
    historical = sf.historic_simulation(reach_id, endpoint=sf.LOCAL_ENDPOINT)
    seasonal = sf.seasonal_average(reach_id, endpoint=sf.LOCAL_ENDPOINT)
    rperiods = sf.return_periods(reach_id, endpoint=sf.LOCAL_ENDPOINT)
    plot_all(stats, ensembles, warnings, records, historical, seasonal, rperiods)
