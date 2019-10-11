===============
geoglows.series
===============

The series module contains functions that will turn the pandas dataframes requested with the streamflow module into
a plotly graph or dictionary containing a plotable series of values.

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