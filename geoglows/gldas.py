try:
    import pandas
    import requests
    import json
    from io import StringIO
except ImportError as error:
    raise error

TETHYS_ENDPOINT = 'https://tethys.byu.edu/apps/gldas/api/'
SAMPLE_TOKEN = 'Token 6836afb1cc45752e8e4541595c6d32a68a4d70d4'


def help(apikey=SAMPLE_TOKEN):
    headers = {'Authorization': apikey}
    data = requests.get(TETHYS_ENDPOINT + 'help', headers=headers).text
    return json.loads(data)


def point_timeseries(time, variable, lat, lon, apikey=SAMPLE_TOKEN):
    params = {
        'time': time,
        'variable': variable,
        'location': [lon, lat]
    }
    headers = {'Authorization': apikey}
    data = requests.get(TETHYS_ENDPOINT + 'timeseries', headers=headers, params=params).text
    return json.loads(data)


def box_timeseries(time, variable, minlat, maxlat, minlon, maxlon, apikey=SAMPLE_TOKEN):
    params = {
        'time': time,
        'variable': variable,
        'location': [minlon, maxlon, minlat, maxlat]
    }
    headers = {'Authorization': apikey}
    data = requests.get(TETHYS_ENDPOINT + 'timeseries', headers=headers, params=params).text
    return json.loads(data)


def region_timeseries(time, variable, region, apikey=SAMPLE_TOKEN):
    params = {
        'time': time,
        'variable': variable,
        'location': region
    }
    headers = {'Authorization': apikey}
    data = requests.get(TETHYS_ENDPOINT + 'timeseries', headers=headers, params=params).text
    return json.loads(data)
