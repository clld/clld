from __future__ import unicode_literals, print_function, division, absolute_import

from zope.interface import (
    Interface,
    Attribute,
)


class ICldfDataset(Interface):
    def write(request, archive):
        """Write the files making up the CLDF dataset to a zip archive."""


# ---------------------------------------------------------------------------
# Interfaces for model classes
# ---------------------------------------------------------------------------
class IDataset(Interface):

    """marker."""


class IFile(Interface):

    """marker."""


class ILanguage(Interface):
    name = Attribute('')
    latitude = Attribute('')
    longitude = Attribute('')


class ISentence(Interface):

    """marker."""


class ISource(Interface):

    """marker."""


class IParameter(Interface):

    """marker."""


class IValueSet(Interface):

    """marker."""


class IValue(Interface):

    """marker."""


class IContribution(Interface):

    """marker."""


class IContributor(Interface):

    """marker."""


class IDomainElement(Interface):

    """marker."""


class IUnitParameter(Interface):

    """marker."""


class IUnit(Interface):

    """marker."""


class IUnitValue(Interface):

    """marker."""


class IUnitDomainElement(Interface):

    """marker."""


class ICombination(Interface):

    """marker."""

    pass


# ---------------------------------------------------------------------------
# Interfaces for pluggable functionality
# ---------------------------------------------------------------------------
class IRepresentation(Interface):
    mimetype = Attribute('')
    charset = Attribute('')
    extension = Attribute('')

    def render(request):
        """ """

    def render_to_response(request):
        """ """


class IIndex(Interface):
    mimetype = Attribute('')
    charset = Attribute('')
    extension = Attribute('')

    def render(request, query, count):
        """ """

    def render_to_response(request, query, count):
        """ """


class IMetadata(Interface):

    """marker."""


class IDownload(Interface):
    name = Attribute('name the download will be registered for')

    def url(request):
        """called from the template for the download page."""

    def create(request):
        """called from the script creating all downloads."""


class IDataTable(Interface):
    model = Attribute('model class of the objects listed in the table')

    def get_query(request, model, **kw):
        """called to retrieve a filtered and sorted sqla query."""


class IMap(Interface):

    """marker."""


class IMenuItems(Interface):

    """marker."""


class IMapMarker(Interface):

    """utility."""

    def __call__(self, ctx, req):
        """Return URL for a marker to use in maps."""


class IIcon(Interface):

    """utility to map icon names to URLs."""

    name = Attribute('name of the icon')

    def url(self, req):
        """return URL for the marker."""


class IIconList(Interface):

    """utility listing all available icons ordered by preference."""


class IFrequencyMarker(Interface):

    """utility."""

    def __call__(self, ctx, req):
        """return URL for an icon to use as marker for frequency."""


class ILinkAttrs(Interface):

    """utility to customize attributes for HTML links to objects."""

    def __call__(self, req, obj, **kw):
        """return dictionary of attributes for link creation."""


class ICtxFactoryQuery(Interface):

    """utility."""

    def __call__(self, model, req):
        """modified query."""


class IOlacConfig(Interface):

    """configuration of an applications OLAC repository."""

    scheme = Attribute('oai-pmh identifier scheme')
    delimiter = Attribute('oai-pmh identifier delimiter')

    def get_earliest_record(self, req):
        """ """

    def get_record(self, req, identifier):
        """ """

    def query_records(self, req, from_=None, until=None):
        """ """

    def format_identifier(self, req, id_):
        """ """

    def parse_identifier(self, req, id_):
        """ """


class IBlog(Interface):

    """utility to integrate a blog."""

    def feed_url(self, ctx, req):
        """return URL of the comment feed for an object (or None)."""

    def post_url(self, ctx, req):
        """return URL of a corresponding post."""


class IStaticResource(Interface):

    """A resource to be linked from the app template."""

    type = Attribute('js or css')
    asset_spec = Attribute('asset spec to be passed to request.static_url')
