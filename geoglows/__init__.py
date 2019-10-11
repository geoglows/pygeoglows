# each of the api methods
from .streamflow import forecast_stats
from .streamflow import forecast_ensembles
from .streamflow import historic_simulation
from .streamflow import return_periods
from .streamflow import seasonal_average
from .streamflow import available_regions
from .streamflow import available_dates

# series processors
from .series import forecasted
from .series import historical
from .series import daily_avg
from .series import probabilities_table
from .series import hydroviewer_forecast
