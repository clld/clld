from zope.interface import (
    Interface,
    Attribute,
)


#----------------------------------------------------------------------------
# Interfaces for model classes
#----------------------------------------------------------------------------
class IDataset(Interface):
    """
    """


class IFile(Interface):
    """
    """


class ILanguage(Interface):
    name = Attribute('')
    latitude = Attribute('')
    longitude = Attribute('')


class ISentence(Interface):
    """marker interface
    """


class ISource(Interface):
    """marker interface
    """


class IParameter(Interface):
    """marker interface
    """


class IValueSet(Interface):
    """marker interface
    """


class IValue(Interface):
    """marker interface
    """


class IContribution(Interface):
    """marker interface
    """


class IContributor(Interface):
    """marker interface
    """


class IDomainElement(Interface):
    """marker interface
    """


class IUnitParameter(Interface):
    """marker interface
    """


class IUnit(Interface):
    """marker interface
    """


class IUnitValue(Interface):
    """marker interface
    """


class IUnitDomainElement(Interface):
    """marker interface
    """


class ICombination(Interface):
    """marker interface
    """


#----------------------------------------------------------------------------
# Interfaces for pluggable functionality
#----------------------------------------------------------------------------
class IRepresentation(Interface):
    """
    """
    mimetype = Attribute('')
    charset = Attribute('')
    extension = Attribute('')

    def render(request):
        """
        """

    def render_to_response(request):
        """
        """


class IIndex(Interface):
    """
    """
    mimetype = Attribute('')
    charset = Attribute('')
    extension = Attribute('')

    def render(request, query, count):
        """
        """

    def render_to_response(request, query, count):
        """
        """


class IMetadata(Interface):
    """
    """


class IDownload(Interface):
    """
    """
    name = Attribute('name the download will be registered for')

    def url(request):
        """called from the template for the download page
        """

    def create(request):
        """called from the script creating all downloads
        """


class IDataTable(Interface):
    """marker
    """


class IMap(Interface):
    """marker
    """


class IMenuItems(Interface):
    """marker interface
    """


class IMapMarker(Interface):
    """utility
    """
    def __call__(self, ctx, req):
        """
        :return: URL for a marker to use in maps.
        """


class IIcon(Interface):
    """utility to map icon names to URLs
    """
    name = Attribute('name of the icon')

    def url(self, req):
        """
        :return: URL for the marker
        """


class IFrequencyMarker(Interface):
    """utility
    """
    def __call__(self, ctx, req):
        """
        :return: URL for an icon to use as marker for frequency.
        """


class ILinkAttrs(Interface):
    """utility to customize attributes for HTML links to objects.
    """
    def __call__(self, req, obj, **kw):
        """
        :return: dictionary of attributes for link creation.
        """


class ICtxFactoryQuery(Interface):
    """utility
    """
    def __call__(self, model, req):
        """
        :return: URL for a marker to use in maps.
        """


class IOlacConfig(Interface):
    """utility class bundling all configurable aspects of an applications OLAC repository
    """
    scheme = Attribute('oai-pmh identifier scheme')
    delimiter = Attribute('oai-pmh identifier delimiter')

    def get_earliest_record(self, req):
        """
        """

    def get_record(self, req, identifier):
        """
        """

    def query_records(self, req, from_=None, until=None):
        """
        """

    def format_identifier(self, req, id_):
        """
        """

    def parse_identifier(self, req, id_):
        """
        """


class IBlog(Interface):
    """utility to integrate a blog
    """
    def feed_url(self, ctx, req):
        """
        :return: URL of the comment feed for an object (or None)
        """

    def post_url(self, ctx, req):
        """
        :return: URL of the comment feed for an object (or None)
        """
