import geoglows.streamflow as sf

endpoint = 'http://0.0.0.0:8090/api/'
reach_id = 3000150
region = 'japan-geoglows'

stats = sf.forecast_stats(reach_id, endpoint=endpoint)
ensembles = sf.forecast_ensembles(reach_id, endpoint=endpoint)
warnings = sf.forecast_warnings(region, endpoint=endpoint)
records = sf.forecast_records(reach_id, endpoint=endpoint)

historical_int = sf.historic_simulation(reach_id, forcing='era_interim', endpoint=endpoint)
historical_5 = sf.historic_simulation(reach_id, forcing='era_5', endpoint=endpoint)

seasonal_int = sf.seasonal_average(reach_id, forcing='era_interim', endpoint=endpoint)
seasonal_5 = sf.seasonal_average(reach_id, forcing='era_5', endpoint=endpoint)

rperiods_int = sf.return_periods(reach_id, forcing='era_interim', endpoint=endpoint)
rperiods_5 = sf.return_periods(reach_id, forcing='era_5', endpoint=endpoint)

print(stats.head())
print(ensembles.head())
print(warnings.head())
print(records.head())

print(historical_int.head())
print(historical_5.head())
print(seasonal_int.head())
print(seasonal_5.head())
print(rperiods_int.head())
print(rperiods_5.head())
