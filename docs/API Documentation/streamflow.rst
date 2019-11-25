==========
streamflow
==========

The streamflow module contains functions for getting streamflow data from the GEOGloWS model (`REST API Functions`_),
for turning them into useful plots (`Series Processing Functions`_), and some additional `Utilities`_. Also check the
`FAQ`_ section.

REST API Functions
~~~~~~~~~~~~~~~~~~
The streamflow module provides a series of functions for requesting forecasted and historical data from the GEOGloWS
ECMWF Streamflow Service. This data is available from this service through a REST API. Simply put, a REST API is a way
to get information over the internet without using a web browser.

In general, a method requires an ID, called the reach_id or common id (COMID), for a specific stream. This ID is unique
to the stream network configured for this Service. It is arbitrarily assigned so that there is a way to keep data
organized. Get it using the function.

forecast_stats
--------------

.. automodule:: geoglows.streamflow
    :members:
        forecast_stats
    :noindex:

forecast_ensembles
------------------

.. automodule:: geoglows.streamflow
    :members:
        forecast_ensembles
    :noindex:

historic_simulation
-------------------

.. automodule:: geoglows.streamflow
    :members:
        historic_simulation
    :noindex:

seasonal_average
----------------

.. automodule:: geoglows.streamflow
    :members:
        seasonal_average
    :noindex:

return_periods
--------------

.. automodule:: geoglows.streamflow
    :members:
        return_periods
    :noindex:

available_dates
---------------

.. automodule:: geoglows.streamflow
    :members:
        available_dates
    :noindex:

available_regions
-----------------

.. automodule:: geoglows.streamflow
    :members:
        available_regions
    :noindex:

Series Processing Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following functions turn the results of the API functions into plots or easily plotable data. These produce
dictionaries, plotly python objects (compatible with showing plots in notebooks), or plotly html code to use in web
applications.

forecast_plot
-------------

.. automodule:: geoglows.streamflow
    :members:
        forecast_plot
    :noindex:

ensembles_plot
--------------

.. automodule:: geoglows.streamflow
    :members:
        ensembles_plot
    :noindex:

historic_plot
-------------

.. automodule:: geoglows.streamflow
    :members:
        historical_plot
    :noindex:

seasonal_plot
-------------

.. automodule:: geoglows.streamflow
    :members:
        seasonal_plot
    :noindex:

flow_duration_curve_plot
------------------------

.. automodule:: geoglows.streamflow
    :members:
        flow_duration_curve_plot
    :noindex:

probabilities_table
-------------------

.. automodule:: geoglows.streamflow
    :members:
        probabilities_table
    :noindex:


Utilities
~~~~~~~~~
Miscellaneous functions to help with interacting with the streamflow REST API.

reach_to_region
---------------

.. automodule:: geoglows.streamflow
    :members:
        reach_to_region
    :noindex:

latlon_to_reach
---------------

.. automodule:: geoglows.streamflow
    :members:
        latlon_to_reach
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
