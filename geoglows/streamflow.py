import json
import warnings
from io import StringIO

import pandas as pd
import requests

ENDPOINT = 'https://geoglows.ecmwf.int/api/'

DEPRECATIONWARNING = """
The streamflow module is deprecated and will be removed early 2025 when GEOGLOWS Model V1 is removed. These functions 
will no longer be updated and they will not work with the latest model and datasets. Please upgrade to GEOGLOWS Model V2 
and update your code to use the geoglows.data module's analogous functions. Visit https://data.geoglows.org for more 
information and tutorials to help you transition.
"""

__all__ = ['forecast_stats', 'forecast_ensembles', 'forecast_warnings', 'forecast_records', 'historic_simulation',
           'daily_averages', 'monthly_averages', 'return_periods', 'available_dates', ]


# FUNCTIONS THAT CALL THE GLOBAL STREAMFLOW PREDICTION API
def forecast_stats(reach_id: int, return_format: str = 'csv', forecast_date: str = None,
                   endpoint: str = ENDPOINT, s: requests.Session = False) -> pd.DataFrame:
    """
    Retrieves statistics that summarize the ensemble streamflow forecast for a certain reach_id

    Args:
        reach_id: the ID of a stream
        return_format: 'csv', 'json', 'waterml', 'url'
        forecast_date: a string specifying the date to request in YYYYMMDD format
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = streamflow.rst.forecast_stats(12341234)
    """
    warnings.warn(DEPRECATIONWARNING, DeprecationWarning)
    method = 'ForecastStats/'

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}'
    params = {'reach_id': reach_id, 'return_format': return_format}
    if forecast_date is not None:
        params["date"] = forecast_date
    # return the requested data
    return _make_request(endpoint, method, params, return_format, s)


def forecast_ensembles(reach_id: int, return_format: str = 'csv', forecast_date: str = None,
                       endpoint: str = ENDPOINT, s: requests.Session = False) -> pd.DataFrame:
    """
    Retrieves each ensemble from the most recent streamflow forecast for a certain reach_id

    Args:
        reach_id: the ID of a stream
        return_format: 'csv', 'json', 'waterml', 'url'
        forecast_date: a string specifying the date to request in YYYYMMDD format
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = streamflow.rst.forecast_ensembles(12341234)
    """
    warnings.warn(DEPRECATIONWARNING, DeprecationWarning, stacklevel=2)
    method = 'ForecastEnsembles/'

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}'

    params = {'reach_id': reach_id, 'return_format': return_format}
    if forecast_date is not None:
        params["date"] = forecast_date

    # return the requested data
    return _make_request(endpoint, method, params, return_format, s)


def forecast_warnings(region: str = 'all', return_format='csv',
                      endpoint=ENDPOINT, s: requests.Session = False) -> pd.DataFrame:
    """
    Retrieves a csv listing streams likely to experience a return period level flow during the forecast period.

    Args:
        region: the name of a region as shown in the available_regions request
        return_format: 'csv', 'json', 'waterml', 'request', 'url'
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = streamflow.rst.forecast_warnings('australia-geoglows')
    """
    warnings.warn(DEPRECATIONWARNING, DeprecationWarning)
    method = 'ForecastWarnings/'

    # if you only wanted the url, quit here
    if return_format == 'url':
        return endpoint + method + f'?region={region}'

    # return the requested data
    return _make_request(endpoint, method, {'region': region, 'return_format': return_format}, return_format, s)


def forecast_records(reach_id: int, start_date: str = None, end_date: str = None, return_format='csv',
                     endpoint=ENDPOINT, s: requests.Session = False) -> pd.DataFrame:
    """
    Retrieves a csv showing the ensemble average forecasted flow for the year from January 1 to the current date

    Args:
        reach_id: the ID of a stream
        return_format: 'csv', 'json', 'waterml', 'url'
        start_date: a string specifying the earliest date to request in YYYYMMDD format
        end_date: a string specifying the latest date to request in YYYYMMDD format
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = streamflow.rst.forecast_warnings('australia-geoglows')
    """
    warnings.warn(DEPRECATIONWARNING, DeprecationWarning)
    method = 'ForecastRecords/'

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}'

    params = {'reach_id': reach_id, 'return_format': return_format}
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date

    # return the requested data
    return _make_request(endpoint, method, params, return_format, s)


def historic_simulation(reach_id: int, return_format='csv', forcing='era_5',
                        endpoint=ENDPOINT, s: requests.Session = False) -> pd.DataFrame:
    """
    Retrieves a historical streamflow simulation derived from a specified forcing for a certain reach_id

    Args:
        reach_id: the ID of a stream
        return_format: 'csv', 'json', 'waterml', 'url'
        forcing: the runoff dataset used to drive the historic simulation (era_interim or era_5)
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = streamflow.rst.historic_simulation(12341234)
    """
    warnings.warn(DEPRECATIONWARNING, DeprecationWarning)
    method = 'HistoricSimulation/'

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}&forcing={forcing}'

    # return the requested data
    params = {'reach_id': reach_id, 'forcing': forcing, 'return_format': return_format}
    return _make_request(endpoint, method, params, return_format, s)


def daily_averages(reach_id: int, return_format='csv', forcing='era_5',
                   endpoint=ENDPOINT, s: requests.Session = False) -> pd.DataFrame:
    """
    Retrieves the average flow for every day of the year at a certain reach_id.

    Args:
        reach_id: the ID of a stream
        return_format: 'csv', 'json', 'waterml', 'url'
        forcing: the runoff dataset used to drive the historic simulation (era_interim or era_5)
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = streamflow.rst.seasonal_average(12341234)
    """
    warnings.warn(DEPRECATIONWARNING, DeprecationWarning)
    method = 'DailyAverages/'

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}&forcing={forcing}'

    # return the requested data
    params = {'reach_id': reach_id, 'forcing': forcing, 'return_format': return_format}
    return _make_request(endpoint, method, params, return_format, s)


def monthly_averages(reach_id: int, return_format='csv', forcing='era_5',
                     endpoint=ENDPOINT, s: requests.Session = False) -> pd.DataFrame:
    """
    Retrieves the average flow for each month at a certain reach_id.

    Args:
        reach_id: the ID of a stream
        forcing: the runoff dataset used to drive the historic simulation (era_interim or era_5)
        return_format: 'csv', 'json', 'waterml', 'url'
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = streamflow.rst.seasonal_average(12341234)
    """
    warnings.warn(DEPRECATIONWARNING, DeprecationWarning)
    method = 'MonthlyAverages/'

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}&forcing={forcing}'

    # return the requested data
    params = {'reach_id': reach_id, 'forcing': forcing, 'return_format': return_format}
    return _make_request(endpoint, method, params, return_format, s)


def return_periods(reach_id: int, return_format='csv', forcing='era_5',
                   endpoint=ENDPOINT, s: requests.Session = False) -> pd.DataFrame:
    """
    Retrieves the return period thresholds based on a specified historic simulation forcing on a certain reach_id.

    Args:
        reach_id: the ID of a stream
        forcing: the runoff dataset used to drive the historic simulation (era_interim or era_5)
        return_format: 'csv', 'json', 'waterml', 'url'
        endpoint: the endpoint of an api instance
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='csv' returns a pd.DataFrame()
        - return_format='json' returns a json
        - return_format='waterml' returns a waterml string
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = streamflow.rst.return_periods(12341234)
    """
    warnings.warn(DEPRECATIONWARNING, DeprecationWarning)
    method = 'ReturnPeriods/'

    # if you only wanted the url, quit here
    if return_format == 'url':
        return f'{endpoint}{method}?reach_id={reach_id}&forcing={forcing}'

    # return the requested data
    params = {'reach_id': reach_id, 'forcing': forcing, 'return_format': return_format}

    return _make_request(endpoint, method, params, return_format, s)


def available_data(endpoint: str = ENDPOINT, return_format='json', s: requests.Session = False) -> dict or str:
    """
    Returns a dictionary with a key for each available_regions containing the available_dates for that region

    Args:
        endpoint: the endpoint of an api instance
        return_format: 'json' or 'url'
        s: requests.Session instance connected to the api's root url

    Returns:
        dict

    Example:
        .. code-block:: python

            data = streamflow.rst.available_data()

    """
    warnings.warn(DEPRECATIONWARNING, DeprecationWarning)
    method = 'AvailableData/'

    # if you only wanted the url, quit here
    if return_format == 'url':
        return endpoint + method

    # return the requested data
    return _make_request(endpoint, method, {}, return_format, s)


def available_dates(reach_id: int = None, region: str = None, return_format: str = 'json',
                    endpoint: str = ENDPOINT, s: requests.Session = False) -> dict or str:
    """
    Retrieves the list of dates of stored streamflow forecasts. You need to specify either a reach_id or a region.

    Args:
        reach_id: the ID of a stream
        region: the name of a hydrologic region used in the model
        endpoint: the endpoint of an api instance
        return_format: 'json' or 'url'
        s: requests.Session instance connected to the api's root url

    Return Format:
        - return_format='json' *(default)* returns {'available_dates': ['list_of_dates']}
        - return_format='url' returns a url string for using in a request or web browser

    Example:
        .. code-block:: python

            data = streamflow.rst.available_dates(12341234)
    """
    warnings.warn(DEPRECATIONWARNING, DeprecationWarning)
    method = 'AvailableDates/'

    # you need a region for the api call, so the user needs to provide one or a valid reach_id to get it from
    params = {'region': 'africa-geoglows'}
    # if you only wanted the url, quit here
    if return_format == 'url':
        return endpoint + method

    # return the requested data
    return _make_request(endpoint, method, params, return_format, s)


# API AUXILIARY FUNCTION
def _make_request(endpoint: str, method: str, params: dict, return_format: str, s: requests.Session = False):
    if return_format == 'request':
        params['return_format'] = 'csv'

    # request the data from the API
    if s:
        data = s.get(endpoint + method, params=params)
    else:
        data = requests.get(endpoint + method, params=params)
    if data.status_code != 200:
        raise RuntimeError('Recieved an error from the Streamflow REST API: ' + data.text)

    # process the response from the API as appropriate to make the corresponding python object
    if return_format == 'csv':
        tmp = pd.read_csv(StringIO(data.text), index_col=0)
        if 'z' in tmp.columns:
            del tmp['z']
        if method in ('ForecastWarnings/', 'ReturnPeriods/', 'DailyAverages/', 'MonthlyAverages/'):
            return tmp
        if method == 'SeasonalAverage/':
            tmp.index = pd.to_datetime(tmp.index + 1, format='%j').strftime('%b %d')
            return tmp
        tmp.index = pd.to_datetime(tmp.index)
        return tmp
    elif return_format == 'json':
        return json.loads(data.text)
    elif return_format == 'waterml':
        return data.text
    else:
        raise ValueError(f'Unsupported return format requested: {return_format}')
