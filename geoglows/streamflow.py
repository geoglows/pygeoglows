try:
    import pandas
    import requests
    import json
    from io import StringIO
except ImportError as error:
    raise error

AZURE_ENDPOINT = 'http://global-streamflow-prediction.eastus.azurecontainer.io/api/'
RETURN_FORMATS = ['csv', 'json', 'waterml']


def forecast_stats(reach_id, apikey, return_format='csv'):
    params = {
        'reach_id': reach_id,
        'return_format': return_format
    }
    headers = {'Ocp-Apim-Subscription-Key': apikey}

    data = requests.get(AZURE_ENDPOINT + 'ForecastStats', headers=headers, params=params).text

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data))
    elif return_format == 'json':
        return json.loads(data)
    elif return_format == 'waterml':
        return data


def forecast_ensembles(reach_id, apikey, return_format='csv'):
    params = {
        'reach_id': reach_id,
        'return_format': return_format
    }
    headers = {'Ocp-Apim-Subscription-Key': apikey}

    data = requests.get(AZURE_ENDPOINT + 'ForecastEnsembles', headers=headers, params=params).text

    if return_format == 'csv':
        tmp = pandas.read_csv(StringIO(data), index_col='datetime')
        tmp.index = pandas.to_datetime(tmp.index)
        return tmp
    elif return_format == 'json':
        return json.loads(data)
    elif return_format == 'waterml':
        return data


def historic_simulation(reach_id, apikey, return_format='csv'):
    params = {
        'reach_id': reach_id,
        'region': 'south_asia-mainland',
        'return_format': return_format
    }
    headers = {'Ocp-Apim-Subscription-Key': apikey}

    data = requests.get(AZURE_ENDPOINT + 'HistoricSimulation', headers=headers, params=params).text

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data))
    elif return_format == 'json':
        return json.loads(data)
    elif return_format == 'waterml':
        return data


def seasonal_average(reach_id, apikey, return_format='csv'):
    params = {
        'reach_id': reach_id,
        'region': 'south_asia-mainland',
        'return_format': return_format
    }
    headers = {'Ocp-Apim-Subscription-Key': apikey}

    data = requests.get(AZURE_ENDPOINT + 'SeasonalAverage', headers=headers, params=params).text

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data))
    elif return_format == 'json':
        return json.loads(data)
    elif return_format == 'waterml':
        return data


def return_periods(reach_id, apikey, return_format='csv'):
    params = {
        'reach_id': reach_id,
        'region': 'south_asia-mainland',
        'return_format': return_format
    }
    headers = {'Ocp-Apim-Subscription-Key': apikey}

    data = requests.get(AZURE_ENDPOINT + 'ReturnPeriods', headers=headers, params=params).text

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data), index_col='return period')
    elif return_format == 'json':
        return json.loads(data)
    elif return_format == 'waterml':
        return data


def available_regions(apikey):
    headers = {'Ocp-Apim-Subscription-Key': apikey}
    return json.loads(requests.get(AZURE_ENDPOINT + 'AvailableRegions', headers=headers).text)


def available_dates(apikey):
    headers = {'Ocp-Apim-Subscription-Key': apikey}
    return json.loads(requests.get(AZURE_ENDPOINT + 'ReturnPeriods', headers=headers).text)
