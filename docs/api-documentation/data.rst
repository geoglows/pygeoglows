=============
geoglows.data
=============

The data module provides functions for requesting forecasted and historical data river discharge simulations.
The data can be retrieved from the REST data service hosted by ECMWF or it can be retrieved from the repository sponsored
by the AWS Open Data Program. The speed and reliability of the AWS source is typically better than the REST service.

In general, each function requires a river ID. The name for the ID varies based on the streams network dataset. It is called
LINKNO in GEOGLOWS which uses the TDX-Hydro streams dataset. This is the same as a reach_id or common id (COMID) used previously.
To find a LINKNO (river ID number), please refer to https://data.geoglows.org and browse the tutorials.

Forecasted Streamflow
---------------------

.. automodule:: geoglows.data
	:members:
		forecast, forecast_stats, forecast_ensembles, forecast_records
	:noindex:

Historical Simulation
---------------------

.. automodule:: geoglows.data
    :members:
        retrospective, return_periods, annual_averages, monthly_averages, daily_averages,
    :noindex:

GEOGLOWS Model Utilities
------------------------

.. automodule:: geoglows.data
    :members:
        metadata_tables
    :noindex:
