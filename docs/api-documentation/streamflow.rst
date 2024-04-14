===================
geoglows.streamflow
===================

THIS MODULE IS DEPRECATED. Please update your code to use the new GEOGLOWS model and data services. Analogous functions
to everything in this module is found in the `geoglows.data` or `geoglows.streams` modules.

The streamflow module provides a series of functions for requesting forecasted and historical data from the GEOGLOWS
ECMWF Streamflow Service for Model and Data Services Version 1.

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

GEOGLOWS Model Utilities
------------------------

.. automodule:: geoglows.streamflow
    :members:
        available_dates
    :noindex: