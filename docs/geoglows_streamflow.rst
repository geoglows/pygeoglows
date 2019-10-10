===================
geoglows.streamflow
===================

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

    from geoglows.streamflow import forecast_stats

    data = forecast_stats(12341234, 'my_api_token', return_format='csv')

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

    from geoglows.streamflow import forecast_ensembles

    data = forecast_ensembles(12341234, 'my_api_token', return_format='csv')

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

    from geoglows.streamflow import historic_simulation

    data = historic_simulation(12341234, 'my_api_token', return_format='csv')

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

    from geoglows.streamflow import seasonal_average

    data = seasonal_average(12341234, 'my_api_token', return_format='csv')

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

    from geoglows.streamflow import return_periods

    data = return_periods(12341234, 'my_api_token')

available_regions
-----------------
Returns a dictionary with a list of the names of regions currently supported by the GSP API.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    from geoglows.streamflow import available_regions

    data = available_regions('my_api_token')

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

    from geoglows.streamflow import available_dates

    data = available_dates('my_api_token')
