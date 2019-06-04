import warnings

from clldutils.color import *

warnings.simplefilter('always', DeprecationWarning)
warnings.warn(
    "color module has moved to clldutils, import from there!", category=DeprecationWarning)
warnings.simplefilter('default', DeprecationWarning)
