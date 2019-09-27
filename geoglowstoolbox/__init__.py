# each of the api methods
from .streamflow_api import forecast_stats
from .streamflow_api import forecast_ensembles
from .streamflow_api import historic_simulation
from .streamflow_api import return_periods
from .streamflow_api import seasonal_average
from .streamflow_api import available_regions
from .streamflow_api import available_dates

# and some auxiliary functions
from .streamflow_api import validate_parameters
from .streamflow_api import reach_to_region

# series processors
from .series import forecasted
from .series import historical
from .series import daily_avg
from .series import probabilities_table
