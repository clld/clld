from zope.interface import implementer, implements
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
    '66ff33',
    '990099',
    '9999ff',
    '99ffff',
    'aa0000',
    'cccccc',
    'dd0000',
    'e8e8e8',
    'ed9c07',
    'efe305',
    'f3ffb0',
    'fe3856',
    'ff0000',
    'ff00ff',
    'ff4400',
    'ff6600',
    'ffcc00',
    'ffff00',
    'ffffcc',
    'ffffff',
]


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


@implementer(IMapMarker)
class MapMarker(object):
    """The default map marker is an orange circle
    """
    def __call__(self, ctx, req):
        return req.registry.getUtility(IIcon, 'cff6600').url(req)
