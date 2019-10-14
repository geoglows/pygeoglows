===================
geoglows.streamflow
===================

API Functions
~~~~~~~~~~~~~

The streamflow module contains functions that will request data from the Global Streamflow Prediction service sponsored
by Microsoft's AI for Earth program. The functions in this package directly parallel the methods available from the
API.

forecast_stats
--------------
Retrieves statistics of the ensemble-forecasted streamflow of a specific reach_id. The forecasted streamflow is based
on an ensemble of 52 members. The statistics include min, mean, max, one standard deviation above and below the mean,
and the high resolution forecast.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| reach_id        | The ID of a stream.                                    | 2004351 (integer)        |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+
| return_format   | csv (pandas DF), json (dictionary), waterml (string)   | default: csv             |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.forecast_stats(12341234, 'my_api_token', return_format='csv')

forecast_ensembles
------------------
Returns a table of the forecasted streamflow made by each of the 52 members.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| reach_id        | The ID of a stream.                                    | 2004351 (integer)        |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+
| return_format   | csv (pandas DF), json (dictionary), waterml (string)   | default: csv             |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.forecast_ensembles(12341234, 'my_api_token', return_format='csv')

historic_simulation
-------------------
Returns a timeseries of simulated streamflow for the reach based on the ERA Interim dataset.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| reach_id        | The ID of a stream.                                    | 2004351 (integer)        |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+
| return_format   | csv (pandas DF), json (dictionary), waterml (string)   | default: csv             |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.historic_simulation(12341234, 'my_api_token', return_format='csv')

seasonal_average
----------------
Returns a timeseries of the average streamflow for each day of the year based on the 35 year historical simulation.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| reach_id        | The ID of a stream.                                    | 2004351 (integer)        |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+
| return_format   | csv (pandas DF), json (dictionary), waterml (string)   | default: csv             |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.seasonal_average(12341234, 'my_api_token', return_format='csv')

return_periods
--------------
Returns a dictionary with the streamflows corresponding to a 2, 10, and 20 year event for a specific stream.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| reach_id        | The ID of a stream.                                    | 2004351 (integer)        |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.return_periods(12341234, 'my_api_token')

available_regions
-----------------
Returns a dictionary with a list of the names of regions currently supported by the GSP API.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.available_regions('my_api_token')

available_dates
---------------
Returns the date of the dates of forecasts currently available from the API. Currently, only the most recent/current
day is cached by the API.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.streamflow.available_dates('my_api_token')

Series Processors
~~~~~~~~~~~~~~~~~

The streamflow module also contains functions that will turn the pandas dataframes generated from the API functions
into a plotly graph or dictionary containing a plotable series of values.

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