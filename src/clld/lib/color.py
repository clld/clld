import warnings

from clldutils.color import *  # noqa: F401, F403

warnings.simplefilter('always', DeprecationWarning)
warnings.warn(
    "color module has moved to clldutils, import from there!", category=DeprecationWarning)
warnings.simplefilter('default', DeprecationWarning)
