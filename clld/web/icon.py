from itertools import product

from zope.interface import implementer
from clld.interfaces import IIcon, IMapMarker


SHAPES = [
    "c",  # circle
    "s",  # square
    "t",  # triangle (pyramid)
    "f",  # inverted pyramid
    "d",  # diamond
]

COLORS = [
    '000000',
    '0000dd',
    '0000ff',
    '009900',
    '00ff00',
    '00ffff',
    '4d6cee',
    '66ff33',
    '990099',
    '9999ff',
    '99ffff',
    'a0fb75',
    'aa0000',
    'cb9a34',
    'cccccc',
    'd22257',
    'dd0000',
    'e8e8e8',
    'ed9c07',
    'efe305',
    'f38847',
    'f3ffb0',
    'fe3856',
    'ff0000',
    'ff00ff',
    'ff4400',
    'ff6600',
    'ff66ff',
    'ffcc00',
    'ffff00',
    'ffffcc',
    'ffffff',
]

# the following colors show enough mutual contrast to be easily distinguised:
PREFERED_COLORS = [
    '0000dd',
    '009900',
    '990099',
    'dd0000',
    'ffff00',
    'ffffff',
    '00ff00',
    '00ffff',
    'cccccc',
    'ff6600',
]
SECONDARY_COLORS = [c for c in COLORS if c not in PREFERED_COLORS]


@implementer(IIcon)
class Icon(object):
    """default implementation of IIcon: Icons are static image files.
    """
    def __init__(self, name):
        self.name = name

    @property
    def asset_spec(self):
        return 'clld:web/static/icons/%s.png' % self.name

    def url(self, req):
        return req.static_url(self.asset_spec)


ICONS = map(Icon, ['%s%s' % (s, c) for s in SHAPES for c in COLORS])
ICON_MAP = {icon.name: icon for icon in ICONS}
ORDERED_ICONS = [ICON_MAP[s + c] for s, c in
                 list(product(SHAPES, PREFERED_COLORS)) +
                 list(product(SHAPES, SECONDARY_COLORS))]


@implementer(IMapMarker)
class MapMarker(object):
    """The default map marker is an orange circle
    """
    def __call__(self, ctx, req):
        return req.registry.getUtility(IIcon, 'cff6600').url(req)
