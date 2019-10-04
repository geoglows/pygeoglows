try:
    import pandas
    import numpy
    import requests
except ImportError as error:
    raise error

FORECAST_STAT_TYPES = ['all', 'mean', 'min', 'max', 'high_res', 'std_dev_range_upper', 'std_dev_range_lower']


def forecasted(reachid=None, forecast=None, apikey=None, returnformat=0):
    return


def historical(reachid=None, apikey=None, returnformat=0):
    return


def daily_avg(reachid=None, apikey=None, returnformat=0):
    return


def probabilities_table(reachid=None, apikey=None, returnformat=0):
    return
