"""Functionality to manage icons for map markers."""
import itertools

from clldutils import svg
from clldutils.color import rgb_as_hex
from zope.interface import implementer

from clld.interfaces import IIcon, IMapMarker, IValue, IValueSet, IDomainElement

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
DEFAULT_ICON = 'cff6600'

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

    """Default implementation of IIcon: Icons are static image files."""

    def __init__(self, name, opacity=None, select_id=None):
        self.name = name
        self.opacity = opacity
        self.select_id = select_id

    @classmethod
    def from_req(cls,
                 ctx,
                 req,
                 icon_spec_factory=None,
                 icon_map=None):
        from clld.db.models.common import CombinationDomainElement  # Avoid circular imports.

        de, icon, opacity, select_id = None, None, '1.0', None
        icon_map = icon_map or {}

        if IValue.providedBy(ctx):
            de = ctx.domainelement
        elif IValueSet.providedBy(ctx):
            de = ctx.values[0].domainelement
        elif IDomainElement.providedBy(ctx):
            de = ctx
        elif isinstance(ctx, CombinationDomainElement):
            select_id = 'v' + ctx.id
            icon = req.params.get(select_id, ctx.icon.name)

        if de:
            select_id = 'v{}'.format(de.number)
            icon = req.params.get(select_id, de.jsondata['icon'])

        if not icon and icon_spec_factory:
            icon = icon_spec_factory(ctx, req)
            if isinstance(icon, tuple):
                icon, select_id = icon

        if icon:
            opacity = None
            if "'" in icon:
                icon = icon.split("'")[0]
            if len(icon) > 4:
                if len(icon) == 9:
                    opacity = int('0x' + icon[7:], base=16) / 255
                    icon = icon[:7]
                elif len(icon) == 7:
                    pass
                else:
                    icon = icon[:4]
            if len(icon) == 4:
                icon = icon[0] + 2 * icon[1] + 2 * icon[2] + 2 * icon[3]
            return cls(icon_map.get(icon, icon), opacity=opacity, select_id=select_id)

    @property
    def shape(self):
        return self.name[0]

    @property
    def color(self):
        res = rgb_as_hex(self.name[1:7])
        if self.opacity:
            res += hex(round(float(self.opacity) * 255))[2:]
        return res

    def url(self, req):
        return svg.data_url(svg.icon(self.name, opacity=str(self.opacity)))


#: a list of all available icons:
ICONS = [Icon('%s%s' % (s, c)) for s in SHAPES for c in COLORS]

#: a dictionary mapping icon names to icon objects:
ICON_MAP = {icon.name: icon for icon in ICONS}

#: a list of icons ordered by preference:
ORDERED_ICONS = [ICON_MAP[s + c] for s, c in itertools.chain(
                 itertools.product(SHAPES, PREFERED_COLORS),
                 itertools.product(SHAPES, SECONDARY_COLORS))]


@implementer(IMapMarker)
class MapMarker(object):

    """The default map marker is an orange circle."""

    def get_icon(self, ctx, req):
        return DEFAULT_ICON

    def __call__(self, ctx, req):
        icon = self.get_icon(ctx, req) or DEFAULT_ICON
        return req.registry.getUtility(IIcon, icon).url(req)
