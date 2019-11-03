try:
    import pandas
    import requests
    import json
    from io import StringIO
except ImportError as error:
    raise error

TETHYS_ENDPOINT = 'https://tethys.byu.edu/apps/gfs/api/'
SAMPLE_TOKEN = 'Token 6836afb1cc45752e8e4541595c6d32a68a4d70d4'


def help(apikey=SAMPLE_TOKEN):
    headers = {'Authorization': apikey}
    data = requests.get(TETHYS_ENDPOINT + 'help', headers=headers).text
    return json.loads(data)


def variable_levels(variable, apikey=SAMPLE_TOKEN):
    params = {'variable': variable}
    headers = {'Authorization': apikey}
    data = requests.get(TETHYS_ENDPOINT + 'variableLevels', headers=headers, params=params).text
    return json.loads(data)


def point_timeseries(variable, level, lat, lon, apikey=SAMPLE_TOKEN):
    params = {
        'variable': variable,
        'level': level,
        'location': [lon, lat]
    }
    headers = {'Authorization': apikey}
    data = requests.get(TETHYS_ENDPOINT + 'timeseries', headers=headers, params=params).text
    return json.loads(data)


def box_timeseries(variable, level, minlat, maxlat, minlon, maxlon, apikey=SAMPLE_TOKEN):
    params = {
        'variable': variable,
        'level': level,
        'location': [minlon, maxlon, minlat, maxlat]
    }
    headers = {'Authorization': apikey}
    data = requests.get(TETHYS_ENDPOINT + 'timeseries', headers=headers, params=params).text
    return json.loads(data)


def region_timeseries(variable, level, region, apikey=SAMPLE_TOKEN):
    params = {
        'variable': variable,
        'level': level,
        'location': region
    }
    headers = {'Authorization': apikey}
    data = requests.get(TETHYS_ENDPOINT + 'timeseries', headers=headers, params=params).text
    return json.loads(data)
