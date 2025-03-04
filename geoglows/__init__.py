import geoglows.bias
import geoglows._plots as plots
import geoglows.data
import geoglows.analyze
import geoglows.tables
import geoglows.streamflow

from ._constants import set_uri
from ._constants import get_uri

__all__ = [
    'bias', 'plots', 'data', 'analyze', 'tables', 'streamflow',
    'set_uri', 'get_uri'
]
__version__ = '2.0.0'
__author__ = 'Riley Hales'
__license__ = 'BSD 3-Clause Clear License'
