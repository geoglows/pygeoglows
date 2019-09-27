try:
    import pandas
    import numpy
    import requests
    from io import StringIO
except ImportError as error:
    raise error
"""
:parameters
    - reachid: the 10 digit reach number generated as part of the watershed delineation 
        process. Use a GIS or the Streamflow Services Tethys app to get this.
    - apikey: must be obtained with an AI for Earth account or a Tethys account
    - returnformat:
        0 or 'pandas' = pandas dataframe
        1 or 'numpy' = numpy array
"""
# todo find the best practice for validating arguments: e.g. that reachid and apikey are valid
# todo how to correctly program a raise exception

VALID_RETURN_FORMATS = [0, 'pandas', 1, 'numpy']
AZURE_ENDPOINT = 'http://global-streamflow-prediction.eastus.azurecontainer.io/api/'


def forecast_stats(reachid=None, apikey=None, returnformat=0):
    params = validate_parameters(**locals())
    params['region'] = reach_to_region(reachid)

    return pandas.read_csv(StringIO(requests.get(AZURE_ENDPOINT + 'ForecastStats', params=params).text))


def forecast_ensembles(reachid=None, apikey=None, returnformat=0):
    params = validate_parameters(**locals())
    params['region'] = reach_to_region(reachid)

    return pandas.read_csv(StringIO(requests.get(AZURE_ENDPOINT + 'ForecastEnsembles', params=params).text))


def historic_simulation(reachid=None, apikey=None, returnformat=0):
    params = validate_parameters(**locals())
    params['region'] = reach_to_region(reachid)

    return pandas.read_csv(StringIO(requests.get(AZURE_ENDPOINT + 'HistoricSimulation', params=params).text))


def seasonal_average(reachid=None, apikey=None, returnformat=0):
    params = validate_parameters(**locals())
    params['region'] = reach_to_region(reachid)

    return pandas.read_csv(StringIO(requests.get(AZURE_ENDPOINT + 'SeasonalAverage', params=params).text))


def return_periods(reachid=None, apikey=None, returnformat=0):
    params = validate_parameters(**locals())
    params['region'] = reach_to_region(reachid)
    return pandas.read_csv(
        StringIO(requests.get(AZURE_ENDPOINT + 'ReturnPeriods', params=params).text), index_col='return period')


def available_regions(apikey=None, returnformat=0):

    return


def available_dates(apikey=None, returnformat=0):

    return


def validate_parameters(reachid, apikey, returnformat):
    if reachid is None:
        raise ValueError('Specify a ReachID')
    if apikey is None:
        raise ValueError('An API key is required')
    if returnformat not in VALID_RETURN_FORMATS:
        raise ValueError('Invalid return format')

    regionname = reach_to_region(reachid)

    return {
        'reach_id': reachid,
        'region': regionname,
        'token': apikey,
    }


def reach_to_region(reachid=None):
    # australia 200k (renumber to 2M)
    # middle east 600k (renumber to 6M)
    # central america 900k (renumber to 11M)

    # Indonesia 1M
    # ------australia 2M
    # Japan 3M
    # East Asia 4M
    # South Asia 5M
    # ------middle_east 6M
    # Africa 7M
    # Central Asia 8M
    # South America 9M
    # West Asia 10M
    # -------central_america 11M
    # Europe 12M
    # North America 13M

    if reachid < 200000:
        raise ValueError('Reach ID is too small')

    elif reachid < 300000:
        return 'australia-geoglows'
    elif reachid < 700000:
        return 'middle_east-geoglows'
    elif reachid < 1000000:
        return 'central_america-geoglows'

    elif reachid < 2000000:
        return 'indonesia-geoglows'
    # elif reachid < 3000000:
    #     return 'australia-geoglows
    elif reachid < 4000000:
        return 'japan-geoglows'
    elif reachid < 5000000:
        return 'east_asia-geoglows'
    elif reachid < 6000000:
        return 'south_asia-geoglows'
    # elif reachid < 7000000:
    #     return 'middle_east-geoglows'
    elif reachid < 8000000:
        return 'africa-geoglows'
    elif reachid < 9000000:
        return 'central_asia-geoglows'
    elif reachid < 10000000:
        return 'south_america-geoglows'
    elif reachid < 11000000:
        return 'west_asia-geoglows'
    # elif reachid < 12000000:
    #     return 'central_america-geoglows'
    elif reachid < 13000000:
        return 'europe-geoglows'
    elif reachid < 14000000:
        return 'north_america-geoglows'
    else:
        raise ValueError('Reach ID is too large')
