==========
streamflow
==========

The streamflow module contains functions for getting streamflow data from the GEOGloWS model and for turning them into
useful plots. Also check the `FAQ`_ section.

REST API Functions
~~~~~~~~~~~~~~~~~~
The streamflow module provides a series of functions for requesting forecasted and historical data from the GEOGloWS
ECMWF Streamflow Service. This data is available from this service through a REST API. Simply put, a REST API is a way
to get information over the internet without using a web browser.

In general, a method requires an ID, called the reach_id or common id (COMID), for a specific stream. This ID is unique
to the stream network configured for this Service. It is arbitrarily assigned so that there is a way to keep data
organized.

Forecasted Streamflow
---------------------

.. automodule:: geoglows.streamflow
    :members:
        forecast_stats, forecast_ensembles, forecast_warnings, forecast_records

Historically Simulated Streamflow
---------------------------------

.. automodule:: geoglows.streamflow
    :members:
        historic_simulation, seasonal_average, return_periods
    :noindex:

GEOGloWS Model Utilities
------------------------

.. automodule:: geoglows.streamflow
    :members:
        available_data, available_regions, available_dates, reach_to_region, latlon_to_reach, latlon_to_region
    :noindex:

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
