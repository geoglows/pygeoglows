import geoglows.streamflow as sf

reach_id = 3000150
region = 'japan-geoglows'

# print(sf.available_data())
# print(sf.available_regions())
# print(sf.available_dates(region=region))

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

plot = sf.forecast_plot(stats, rperiods_int)
plot.show()
plot = sf.ensembles_plot(ensembles, rperiods_int)
plot.show()
plot = sf.records_plot(records, rperiods_int)
plot.show()
plot = sf.historical_plot(historical_int, rperiods_int)
plot.show()
plot = sf.historical_plot(historical_5, rperiods_int)
plot.show()
plot = sf.seasonal_plot(seasonal_int)
plot.show()
plot = sf.seasonal_plot(seasonal_5)
plot.show()

