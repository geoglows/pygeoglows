import geoglows


def get_forecast_data_with_reach_id_region(reach_id, region, endpoint):
    stats = geoglows.streamflow.forecast_stats(reach_id, endpoint=endpoint)
    ensembles = geoglows.streamflow.forecast_ensembles(reach_id, endpoint=endpoint)
    warnings = geoglows.streamflow.forecast_warnings(region, endpoint=endpoint)
    records = geoglows.streamflow.forecast_records(reach_id, endpoint=endpoint)
    return stats, ensembles, warnings, records


def get_historical_data_with_reach_id(reach_id, endpoint, forcing='era_5'):
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
    geoglows.plots.hydroviewer_plot(records, stats, ensembles, rperiods).show()
    geoglows.plots.forecast_plot(stats, rperiods).show()
    geoglows.plots.ensembles_plot(ensembles, rperiods).show()
    geoglows.plots.records_plot(records, rperiods).show()
    geoglows.plots.historical_plot(historical, rperiods).show()
    geoglows.plots.seasonal_plot(seasonal).show()
    geoglows.plots.flow_duration_curve_plot(historical).show()

    # with open('/Users/riley/spatialdata/prob_table.html', 'w') as f:
    #     f.write(geoglows.streamflow.probabilities_table(stats, ensembles, rperiods))
    # with open('/Users/riley/spatialdata/rper_table.html', 'w') as f:
    #     f.write(geoglows.streamflow.return_periods_table(rperiods))

    print(warnings.head(10))

    return


if __name__ == '__main__':
    reach_id = 3004334
    region = 'japan-geoglows'
    lat = 38.840
    lon = -90.112
    print(geoglows.streamflow.latlon_to_reach(lat, lon))
    exit()

    # stats, ensembles, warnings, records = get_forecast_data_with_reach_id_region(reach_id, region, geoglows.streamflow.LOCAL_ENDPOINT)
    # historical, seasonal, rperiods = get_historical_data_with_reach_id(reach_id, geoglows.streamflow.LOCAL_ENDPOINT)
    # plot_all(stats, ensembles, warnings, records, historical, seasonal, rperiods)

    import requests
    import pandas as pd
    import io

    station = 23187280
    comid = 9004355
    hist = geoglows.streamflow.historic_simulation(comid)
    rperiods = geoglows.streamflow.return_periods(comid)
    # data = requests.get(f'https://www.hydroshare.org/resource/d222676fbd984a81911761ca1ba936bf/data/'
    #                     f'contents/Discharge_Data/{station}.csv').text
    # df = pd.read_csv(io.StringIO(data), index_col=0)
    # df.index = pd.to_datetime(df.index)
    # corrected = geoglows.bias.correct2(hist, df)
    # geoglows.plots.historical_bias_corrected(corrected).show()

    # '''Get Simulated Data'''
    # url = f'https://www.hydroshare.org/resource/d222676fbd984a81911761ca1ba936bf/data/contents/Discharge_Data/{station}.csv'
    #
    # s = requests.get(url, verify=True).text
    #
    # observed_flow = pd.read_csv(io.StringIO(s), index_col=0)
    # observed_flow.index = pd.to_datetime(observed_flow.index)
    #
    # datesDischarge = observed_flow.index.tolist()
    # dataDischarge = observed_flow.iloc[:, 0].values
    # dataDischarge.tolist()
    #
    # if isinstance(dataDischarge[0], str):
    #     dataDischarge = map(float, dataDischarge)
    #
    # observed_df = pd.DataFrame(data=dataDischarge, index=datesDischarge, columns=['Observed Streamflow'])
    #
    # corrected = geoglows.bias.correct_historical_simulation(hist, observed_df)
    # geoglows.plots.historical_bias_corrected(corrected, observed_df, hist, rperiods).show()
