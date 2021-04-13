===================
geoglows.streamflow
===================

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
        historic_simulation, return_periods, daily_averages, monthly_averages
    :noindex:

GEOGloWS Model Utilities
------------------------

.. automodule:: geoglows.streamflow
    :members:
        available_data, available_regions, available_dates, reach_to_region, reach_to_latlon, latlon_to_reach, latlon_to_region
    :noindex:
