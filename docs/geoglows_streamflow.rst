===================
geoglows.streamflow
===================

The streamflow module provides a series of functions for requesting forecasted and historical data from the Global
Streamflow Prediction Service (GSP). Data is available from this service through a REST API. Simply put, a REST API is
a way to get information over the internet without using a web browser. These are designated `GSP REST API Functions`_.

This module also contains a series of functions that will process the data from the GSP API. These produce
dictionaries, plotly python objects (compatible with showing plots in notebooks), or plotly html code to use in web
applications. These are designated `Timeseries Processor Functions`_.

Basics of the GSP:  The GSP Service provides access to the results of a hydrologic model that is run each day. The
model is based on a group of unique weather forecasts known as an ensemble. Each unique precipitation forecast, known
as an ensemble member, produces a unique streamflow forecast. There are 52 members of the ensemble that drives the GSP
each day. The GSP also uses the ERA Interim historical precipitation dataset to produce hindcasted streamflow on each
river.

GSP REST API Functions
~~~~~~~~~~~~~~~~~~~~~~

The GSP REST API functions request data from the Global Streamflow Prediction Service sponsored by Microsoft's AI for
Earth program. The functions in this package directly parallel the methods available from the API. In general, a method
requires an ID, sometimes called common id (COMID) or reach id, for a specific stream. This ID is unique to the stream
network configured for the GSP Service. You can get this using the
`Streamflow Services web app <https://tethys.byu.edu/apps/streamflowservices>`_ which has a map interface where you can
click on a stream and see it's identifier. For more information about the GSP API's methods,
`read the documentation <https://github.com/msouff/gsp_rest_api/blob/master/swagger_doc.yaml>`_

forecast_stats
--------------
Retrieves statistics of the forecasted streamflow in a reach from each of the precipitation forecasts. The statistics
include min, mean, max, one standard deviation above and below the mean, and the high resolution forecast.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (required)  | The ID of a stream.                                    | 2004351 (integer)        |
+----------------------+--------------------------------------------------------+--------------------------+
| apikey (required)    | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| return_format        | csv (pandas DF), json (dictionary), waterml (string)   | default: csv             |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: AI4E_ENDPOINT   |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.forecast_stats(12341234, 'my_api_token', return_format='csv')

forecast_ensembles
------------------
Returns a table of the forecasted streamflow made by each of the 52 members.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (required)  | The ID of a stream.                                    | 2004351 (integer)        |
+----------------------+--------------------------------------------------------+--------------------------+
| apikey (required)    | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| return_format        | csv (pandas DF), json (dictionary), waterml (string)   | default: csv             |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: AI4E_ENDPOINT   |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.forecast_ensembles(12341234, 'my_api_token', return_format='csv')

historic_simulation
-------------------
Returns a timeseries of simulated streamflow for the reach based on the ERA Interim dataset.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (required)  | The ID of a stream.                                    | 2004351 (integer)        |
+----------------------+--------------------------------------------------------+--------------------------+
| apikey (required)    | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| return_format        | csv (pandas DF), json (dictionary), waterml (string)   | default: csv             |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: AI4E_ENDPOINT   |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.historic_simulation(12341234, 'my_api_token', return_format='csv')

seasonal_average
----------------
Returns a timeseries of the average streamflow for each day of the year based on the 35 year historical simulation.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (required)  | The ID of a stream.                                    | 2004351 (integer)        |
+----------------------+--------------------------------------------------------+--------------------------+
| apikey (required)    | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| return_format        | csv (pandas DF), json (dictionary), waterml (string)   | default: csv             |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: AI4E_ENDPOINT   |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.seasonal_average(12341234, 'my_api_token', return_format='csv')

return_periods
--------------
Returns a dictionary with the streamflows corresponding to a 2, 10, and 20 year event for a specific stream.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (required)  | The ID of a stream.                                    | 2004351 (integer)        |
+----------------------+--------------------------------------------------------+--------------------------+
| apikey (required)    | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: AI4E_ENDPOINT   |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.return_periods(12341234, 'my_api_token')

available_regions
-----------------
Returns a dictionary with a list of the names of regions currently supported by the GSP API.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| apikey (required)    | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: AI4E_ENDPOINT   |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.available_regions('my_api_token')

available_dates
---------------
Returns the date of the dates of forecasts currently available from the API. Currently, only the most recent/current
day is cached by the API.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| apikey (required)    | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: AI4E_ENDPOINT   |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.available_dates('my_api_token')

Timeseries Processor Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following functions turn the results of the API functions into plots or easily plotable data

forecasted
----------
Processes the dataframe results of ``streamflow.forecast_stats``, ``streamflow.forecast_ensembles``, and
``streamflow.return_periods`` into a dictionary of the series needed to plot with plotly, or the plotly generated html
code.

historical
----------
Processes the results of ``streamflow.historic_simulation`` and ``streamflow.return_periods`` into a dictionary of the
series needed to plot with plotly, or the plotly generated html code.

daily_avg
---------
Processes the results of ``streamflow.seasonal_average`` into a dictionary of the series needed to plot with plotly, or
the plotly generated html code.

probabilities_table
-------------------
Processes the results of ``streamflow.forecast_stats``, ``streamflow.forecast_ensembles``, and
``streamflow.return_periods`` and uses flask template rendering to generate html code that shows the probabilities of
exceeding the return period flow on each day of the forecast.

hydroviewer_forecast
--------------------
The hydroviewer function returns the HTML needed by the Hydroviewer and Streamflow Services Tethys applications. It
uses the multiprocessing Pool class to asynchronously make all the streamflow api calls. This means the user only needs
to wait as long as the slowest API response rather than the combined time of each API call.