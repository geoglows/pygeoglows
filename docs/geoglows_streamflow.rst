===================
geoglows.streamflow
===================

The streamflow module contains functions for getting streamflow data from the GEOGloWS model (`REST API Functions`_),
for turning them into useful plots (`Series Processing Functions`_), and some additional `Utilities`_. Also check the
`FAQ`_ section.

REST API Functions
~~~~~~~~~~~~~~~~~~
The streamflow module provides a series of functions for requesting forecasted and historical data from the GEOGloWS
ECMWF Streamflow Service. This data is available from this service through a REST API. Simply put, a REST API is a way
to get information over the internet without using a web browser.

The API is currently available from a BYU endpoint and 2 endpoints through Microsoft Azure. These endpoints are string
variables called BYU_ENDPOINT, AI4E_ENDPOINT (requires the api_key parameter) and CONTAINER_ENDPOINT.

In general, a method requires an ID, called the reach_id or common id (COMID), for a specific stream. This ID is unique
to the stream network configured for this Service. It is arbitrarily assigned so that there is a way to keep data
organized. Get it using the `latlon_to_reach`_ function.


forecast_stats
--------------
Retrieves statistics of the forecasted streamflow in a reach from each of the precipitation forecasts. The statistics
include min, mean, max, one standard deviation above and below the mean, and the high resolution forecast.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (recommend) | The ID of a stream.                                    | 204351 (integer)         |
+----------------------+--------------------------------------------------------+--------------------------+
| lat, lon (optional)  | Use lat AND lon instead of reach_id                    | lat=10, lon=10 (integer) |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: BYU_ENDPOINT    |
+----------------------+--------------------------------------------------------+--------------------------+
| api_key              | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| return_format        | pandas (df), json (dictionary), waterml (string)       | default: pandas          |
+----------------------+--------------------------------------------------------+--------------------------+


.. code-block:: python

    # using a reach_id
    data = geoglows.streamflow.forecast_stats(12341234)
    # using lat and lon as keyword arguments instead of reach_id
    data = geoglows.streamflow.forecast_stats(lat=10, lon=10)

forecast_ensembles
------------------
Returns a table of the forecasted streamflow made by each of the 52 members.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (recommend) | The ID of a stream.                                    | 204351 (integer)         |
+----------------------+--------------------------------------------------------+--------------------------+
| lat, lon (optional)  | Use lat AND lon instead of reach_id                    | lat=10, lon=10 (integer) |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: BYU_ENDPOINT    |
+----------------------+--------------------------------------------------------+--------------------------+
| api_key              | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| return_format        | pandas (df), json (dictionary), waterml (string)       | default: pandas          |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    # using a reach_id
    data = geoglows.streamflow.forecast_ensembles(12341234)
    # using lat and lon as keyword arguments instead of reach_id
    data = geoglows.streamflow.forecast_ensembles(lat=10, lon=10)

historic_simulation
-------------------
Returns a timeseries of simulated streamflow for the reach based on the ERA Interim dataset.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (recommend) | The ID of a stream.                                    | 204351 (integer)         |
+----------------------+--------------------------------------------------------+--------------------------+
| lat, lon (optional)  | Use lat AND lon instead of reach_id                    | lat=10, lon=10 (integer) |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: BYU_ENDPOINT    |
+----------------------+--------------------------------------------------------+--------------------------+
| api_key              | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| return_format        | pandas (df), json (dictionary), waterml (string)       | default: pandas          |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

   # using a reach_id
   data = geoglows.streamflow.historic_simulation(12341234)
   # using lat and lon as keyword arguments instead of reach_id
   data = geoglows.streamflow.historic_simulation(lat=10, lon=10)

seasonal_average
----------------
Returns a timeseries of the average streamflow for each day of the year based on the 35 year historical simulation.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (recommend) | The ID of a stream.                                    | 204351 (integer)         |
+----------------------+--------------------------------------------------------+--------------------------+
| lat, lon (optional)  | Use lat AND lon instead of reach_id                    | lat=10, lon=10 (integer) |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: BYU_ENDPOINT    |
+----------------------+--------------------------------------------------------+--------------------------+
| api_key              | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| return_format        | pandas (df), json (dictionary), waterml (string)       | default: pandas          |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

   # using a reach_id
   data = geoglows.streamflow.seasonal_average(12341234)
   # using lat and lon as keyword arguments instead of reach_id
   data = geoglows.streamflow.seasonal_average(lat=10, lon=10)

return_periods
--------------
Returns a dictionary with the streamflows corresponding to a 2, 10, and 20 year event for a specific stream.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (recommend) | The ID of a stream.                                    | 204351 (integer)         |
+----------------------+--------------------------------------------------------+--------------------------+
| lat, lon (optional)  | Use lat AND lon instead of reach_id                    | lat=10, lon=10 (integer) |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: BYU_ENDPOINT    |
+----------------------+--------------------------------------------------------+--------------------------+
| api_key              | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| return_format        | pandas (df), json (dictionary), waterml (string)       | default: pandas          |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

   # using a reach_id
   data = geoglows.streamflow.return_periods(12341234)
   # using lat and lon as keyword arguments instead of reach_id
   data = geoglows.streamflow.return_periods(lat=10, lon=10)

available_dates
---------------
Returns the dates of forecasts currently available from the GEOGloWS model. Currently, only the most recent/current day
is cached by the API. Returns a dictionary. You need to specify either a region or a reach_id.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| region (option 1)    | The name of a global region from `available_regions`_  | europe-geoglows          |
+----------------------+--------------------------------------------------------+--------------------------+
| reach_id (option 2)  | A valid reach_id                                       | 204351                   |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: BYU_ENDPOINT    |
+----------------------+--------------------------------------------------------+--------------------------+
| api_key              | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    data = geoglows.streamflow.available_dates('europe-geoglows')   # using a region name
    data = geoglows.streamflow.available_dates(204351)   # using a reach_id

available_regions
-----------------
Returns a dictionary with a list of the names of regions currently supported by the GSP API.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| api_key              | An API token used to make the request                  | 'alpha_numeric_string'   |
+----------------------+--------------------------------------------------------+--------------------------+
| api_source           | the api endpoint to make requests from                 | default: BYU_ENDPOINT    |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    data = geoglows.streamflow.available_regions()

Series Processing Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following functions turn the results of the API functions into plots or easily plotable data. These produce
dictionaries, plotly python objects (compatible with showing plots in notebooks), or plotly html code to use in web
applications. These are designated

forecast_plot
-------------
Processes the dataframe results of `forecast_stats`_, `forecast_ensembles`_, and `return_periods`_ into a dictionary
of the series needed to plot with plotly, a plotly python object or plotly generated html code.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| stats (required)     | The dataframe returned by `forecast_stats`_            | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| rperiods (required)  | The return periods obtained from `return_periods`_     | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| reach_id (kwarg)     | The reach id to display on the graph title             | 123456789                |
+----------------------+--------------------------------------------------------+--------------------------+
| drain_area (kwarg)   | The upstream drainage area to display on the graph     | String: 536, 187 mi^2    |
+----------------------+--------------------------------------------------------+--------------------------+
| outformat (kwarg)    | format for the plot: json, plotly, plotly_html         | default: plotly          |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    data = geoglows.streamflow.forecast_plot(stats, rperiods, 123456789, outformat='json')

ensembles_plot
--------------
Processes the dataframe results of `forecast_ensembles`_ and `return_periods`_ into a
dictionary of the series needed to plot with plotly, a plotly python object or plotly generated html code.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| ensembles (required) | The dataframe returned by `forecast_ensembles`_        | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| rperiods (required)  | The return periods obtained from `return_periods`_     | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| reach_id (kwarg)     | The reach id to display on the graph title             | 123456789                |
+----------------------+--------------------------------------------------------+--------------------------+
| drain_area (kwarg)   | The upstream drainage area to display on the graph     | String: 536, 187 mi^2    |
+----------------------+--------------------------------------------------------+--------------------------+
| outformat (kwarg)    | format for the plot: json, plotly, plotly_html         | default: plotly          |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    data = geoglows.streamflow.ensembles_plot(stats, rperiods, 123456789, outformat='json')

historic_plot
-------------
Processes the results of `historic_simulation`_ and `return_periods`_ into a dictionary of the
series needed to plot with plotly, or the plotly generated html code.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| hist (required)      | The dataframe returned by `historic_simulation`_       | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| rperiods (required)  | The return periods obtained from `return_periods`_     | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| reach_id (kwarg)     | The reach id to display on the graph title             | 123456789                |
+----------------------+--------------------------------------------------------+--------------------------+
| drain_area (kwarg)   | The upstream drainage area to display on the graph     | String: 536, 187 mi^2    |
+----------------------+--------------------------------------------------------+--------------------------+
| outformat (kwarg)    | format for the plot: json, plotly, plotly_html         | default: plotly          |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    data = geoglows.streamflow.historic_plot(hist, rperiods, 123456789, outformat='json')

seasonal_plot
-------------
Processes the results of `seasonal_average`_ into a dictionary of the series needed to plot with plotly, or
the plotly generated html code.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| seasonal (required)  | The dataframe returned by `seasonal_average`_          | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| rperiods (required)  | The return periods obtained from `return_periods`_     | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| reach_id (kwarg)     | The reach id to display on the graph title             | 123456789                |
+----------------------+--------------------------------------------------------+--------------------------+
| drain_area (kwarg)   | The upstream drainage area to display on the graph     | String: 536, 187 mi^2    |
+----------------------+--------------------------------------------------------+--------------------------+
| outformat (kwarg)    | format for the plot: json, plotly, plotly_html         | default: plotly          |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    data = geoglows.streamflow.seasonal_plot(seasonal, rperiods, 123456789, outformat='json')

flow_duration_curve_plot
------------------------
Processes the results of `historic_simulation`_ and `return_periods`_ into a dictionary of the series needed to plot
with plotly, or the plotly generated html code.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| hist (required)      | The dataframe returned by `historic_simulation`_       | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| reach_id (kwarg)     | The reach id to display on the graph title             | 123456789                |
+----------------------+--------------------------------------------------------+--------------------------+
| drain_area (kwarg)   | The upstream drainage area to display on the graph     | String: 536, 187 mi^2    |
+----------------------+--------------------------------------------------------+--------------------------+
| outformat (kwarg)    | format for the plot: json, plotly, plotly_html         | default: plotly          |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    data = geoglows.streamflow.flow_duration_curve_plot(hist, drain_area='532 km^2', outformat='plotly')

probabilities_table
-------------------
Processes the results of `forecast_stats`_ , `forecast_ensembles`_, and `return_periods`_ and uses jinja2 template
rendering to generate html code that shows the probabilities of exceeding the return period flow on each day of the
forecast.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| stats (required)     | The dataframe returned by `forecast_stats`_            | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| ensembles (required) | The dataframe returned by `forecast_ensembles`_        | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+
| rperiods (required)  | The return periods obtained from `return_periods`_     | pandas.DataFrame         |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    data = geoglows.streamflow.probabilities_table(stats, ensembles, rperiods)

Utilities
~~~~~~~~~
Miscellaneous functions to help with interacting with the streamflow REST API.

reach_to_region
---------------
The geoglows model was prepared by processing terrain data. This was done in smaller segments rather than process the
world's terrain all together. The region may be useful in other applications. Provide a reach_id and it will return a
string with the name of the region that ID falls within.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| reach_id (required)  | The ID of a stream.                                    | 204351 (integer)         |
+----------------------+--------------------------------------------------------+--------------------------+
| lon (required)       | An integer or float longitude value                    | 50                       |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

   region = geoglows.streamflow.reach_to_region(10, 50)

latlon_to_reach
---------------
If you dont know the reach_id for the stream you're interested in, use this function. Provide a latitude and longitude
of a segment of the stream and the code will search an index to find the id of the segment in the model that is closest
to the point you input.

+----------------------+--------------------------------------------------------+--------------------------+
| Parameter            | Description                                            | Examples                 |
+======================+========================================================+==========================+
| lat (required)       | An integer or float latitude value                     | 10                       |
+----------------------+--------------------------------------------------------+--------------------------+
| lon (required)       | An integer or float longitude value                    | 50                       |
+----------------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

   reach_id = latlon_to_reach(10, 50)

FAQ
~~~

How do I save streamflow data to a csv file?
--------------------------------------------
By default, the `REST API Functions`_ that return streamflow data will return a pandas dataframe. You can save those to
a csv with the dataframe's ``.to_csv()`` method.

.. code-block:: python

   # get some data from the geoglows streamflow model
   data = geoglows.streamflow.forecast_stats(12341234)
   # save it to a csv
   data.to_csv('/path/to/save/the/csv/file.csv')
