import geoglows

river_id = 710_456_875

print('dates', geoglows.data.dates())
print('forecast_stats', geoglows.data.forecast(river_id))
print('forecast_stats', geoglows.data.forecast_stats(river_id))
print('forecast_ensembles', geoglows.data.forecast_ensembles(river_id))
print('forecast_records', geoglows.data.forecast_records(river_id))
print('retrospective', geoglows.data.retrospective(river_id))
print('daily_averages', geoglows.data.daily_averages(river_id))
print('monthly_averages', geoglows.data.monthly_averages(river_id))
print('annual_averages', geoglows.data.annual_averages(river_id))
print('return_periods', geoglows.data.return_periods(river_id))

# print('sfdc', geoglows.data.sfdc(river_id))
# print('assigned_sfdc_curve_id', geoglows.data.assigned_sfdc_curve_id(river_id))
# print('sfdc_for_river_id', geoglows.data.sfdc_for_river_id(river_id))
#
# print('metadata_tables', geoglows.data.metadata_tables())
