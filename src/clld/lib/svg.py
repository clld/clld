import warnings

from clldutils.svg import *  # noqa: F401, F403

warnings.simplefilter('always', DeprecationWarning)
warnings.warn("svg module has moved to clldutils, import from there!", category=DeprecationWarning)
warnings.simplefilter('default', DeprecationWarning)
