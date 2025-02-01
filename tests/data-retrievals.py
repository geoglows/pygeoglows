import geoglows

river_id = 710_456_875

print('\n' + '-' * 50 + 'Forecasts')
print('dates', geoglows.data.dates())
print('forecast_stats', geoglows.data.forecast(river_id))
print('forecast_stats', geoglows.data.forecast_stats(river_id))
print('forecast_ensembles', geoglows.data.forecast_ensembles(river_id))
print('forecast_records', geoglows.data.forecast_records(river_id))

print('\n' + '-' * 50 + 'Retrospective')
print('hourly', geoglows.data.retrospective_hourly(river_id))
print('daily', geoglows.data.retrospective_daily(river_id))
print('monthly_timeseries', geoglows.data.retrospective_monthly(river_id))
print('yearly_timeseries', geoglows.data.retrospective_yearly(river_id))
print('return_periods', geoglows.data.return_periods(river_id))
print('annual_maximums', geoglows.data.annual_maximums(river_id))

print('\n' + '-' * 50 + 'Transformers')
print('sfdc', geoglows.data.sfdc(river_id))
print('wse', geoglows.data.wse(river_id))
print('transform_curve_ids', geoglows.data.transform_curve_ids(river_id))
print('sfdc_for_river_id', geoglows.data.sfdc_for_river_id(river_id))
print('wse_for_river_id', geoglows.data.wse_for_river_id(river_id))

print('\n' + '-' * 50 + 'Tables')
print('metadata_tables', geoglows.data.metadata_tables())
print('transform_table', geoglows.data.transform_table())
