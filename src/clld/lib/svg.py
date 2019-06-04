import warnings

from clldutils.svg import *

warnings.simplefilter('always', DeprecationWarning)
warnings.warn("svg module has moved to clldutils, import from there!", category=DeprecationWarning)
warnings.simplefilter('default', DeprecationWarning)
