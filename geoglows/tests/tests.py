import geoglows.streamflow as sf


def request_all_data_with_reach_id_and_region(reach_id, region):
    stats = sf.forecast_stats(reach_id)
    ensembles = sf.forecast_ensembles(reach_id)
    warnings = sf.forecast_warnings(region)
    records = sf.forecast_records(reach_id)

    historical_int = sf.historic_simulation(reach_id, 'era_interim')
    historical_5 = sf.historic_simulation(reach_id, 'era_5')
    seasonal_int = sf.seasonal_average(reach_id, 'era_interim')
    seasonal_5 = sf.seasonal_average(reach_id, 'era_5')
    rperiods_int = sf.return_periods(reach_id, 'era_interim')
    rperiods_5 = sf.return_periods(reach_id, 'era_5')

    return stats, ensembles, warnings, records, historical_int, historical_5, \
           seasonal_int, seasonal_5, rperiods_int, rperiods_5


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


def plot_all(data):
    # does not need warnings
    plot = sf.hydroviewer_plot(data[3], data[0], data[8])
    plot.show()
    plot = sf.forecast_plot(data[0], data[8])
    plot.show()
    plot = sf.ensembles_plot(data[1], data[8])
    plot.show()
    plot = sf.records_plot(data[3], data[8])
    plot.show()
    plot = sf.historical_plot(data[4], data[8])
    plot.show()
    plot = sf.historical_plot(data[5], data[8])
    plot.show()
    plot = sf.seasonal_plot(data[6])
    plot.show()
    plot = sf.seasonal_plot(data[7])
    plot.show()
    return


if __name__ == '__main__':
    reach_id = 3000150
    region = 'japan-geoglows'
    lat = 36.203917
    lon = 139.435292

    data = request_all_data_with_reach_id_and_region(reach_id, region)
    plot_all(data)
    data_latlon = request_all_data_with_lat_lon(lat, lon)
    plot_all(data_latlon)

    # print(stats.head())
    # print(ensembles.head())
    # print(warnings.head())
    # print(records.head())
    # print(historical_int.head())
    # print(historical_5.head())
    # print(seasonal_int.head())
    # print(seasonal_5.head())
    # print(rperiods_int.head())
    # print(rperiods_5.head())
    # print(sf.available_data())
    # print(sf.available_regions())
    # print(sf.available_dates(region=region))
