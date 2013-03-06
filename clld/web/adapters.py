"""
Adaption is used to derive appropriate representations from resources.
"""
from itertools import groupby
from string import Template as StringTemplate
try:
    from simplejson import dumps
except ImportError:
    from json import dumps
import datetime

from zope.interface import implementer, implementedBy
from markupsafe import Markup
from mako.template import Template
from pyramid.response import Response
from pyramid.renderers import render as pyramid_render
from sqlalchemy.orm import object_mapper

from clld import interfaces
from clld.lib import bibtex
from clld.util import flatten_dict

#    "xml":    "application/xml"+CHARSET_SUFFIX,
#    'xhtml':  'text/html'+CHARSET_SUFFIX,
#    "georss": "application/rss+xml"+CHARSET_SUFFIX,
#    "rss": "application/rss+xml"+CHARSET_SUFFIX,
#    "atom":   "application/atom+xml"+CHARSET_SUFFIX,
#    "kml":    "application/vnd.google-earth.kml+xml"+CHARSET_SUFFIX,
#    "rdf":    "application/rdf+xml"+CHARSET_SUFFIX,
#    "json":   "application/json",
#    "osd":    "application/opensearchdescription+xml"+CHARSET_SUFFIX,
# 'ris': application/x-Research-Info-Systems
# 'bib': text/x-bibtex


class Renderable(object):
    """Virtual base class for adapters

    Adapters can provide custom behaviour either by specifying a template to use for
    rendering, or by overwriting the render method.
    """
    template = None
    mimetype = 'text/plain'
    extension = None
    send_mimetype = None

    def __init__(self, obj):
        self.obj = obj

    @property
    def charset(self):
        return 'utf-8' if \
            self.mimetype.startswith('text/') or 'xml' in self.mimetype or 'kml' in self.mimetype \
            else None

    def render_to_response(self, ctx, req):
        res = Response(self.render(ctx, req))
        res.content_type = self.send_mimetype or self.mimetype
        if self.charset:
            res.content_type += '; charset=%s' % self.charset
        return res

    def render(self, ctx, req):
        return pyramid_render(self.template, {'ctx': ctx}, request=req)


@implementer(interfaces.IRepresentation)
class Representation(Renderable):
    """Base class for adapters implementing IRepresentation
    """
    pass


@implementer(interfaces.IIndex)
class Index(Renderable):
    """Base class for adapters implementing IIndex
    """
    pass


@implementer(interfaces.IRepresentation)
class BibTex(Representation):
    """Render a resource's metadata as BibTex record.
    """
    extension = 'bib'
    mimetype = 'text/x-bibtex'
    genre = 'incollection'

    def render(self, ctx, req):
        rec = bibtex.Record(
            self.genre,
            ctx.id,
            title=ctx.name,
            url=req.resource_url(ctx),
            author=[c.name for c in list(ctx.primary_contributors) + list(ctx.secondary_contributors)])
        return rec.serialize()


@implementer(interfaces.IRepresentation)
class TxtCitation(Representation):
    """Render a resource's metadata as plain text string.
    """
    extension = 'txt'
    mimetype = 'text/plain'

    def render(self, ctx, req):
        md = {
            'authors': ', '.join(c.name for c in list(ctx.primary_contributors) + list(ctx.secondary_contributors)),
            'title': ctx.name,
            'url': req.resource_url(ctx),
            'accessed': str(datetime.date.today()),
        }
        for key, value in req.registry.settings.items():
            if key.startswith('clld.publication.'):
                md[key.split('clld.publication.', 1)[1]] = value

        template = StringTemplate(md.get('template', """\
$authors. $year. $title.
In: $editors (eds.)
$sitetitle.
$place: $publisher.
Available online at $url
Accessed on $accessed.
"""))
        return template.safe_substitute(**md)


@implementer(interfaces.IRepresentation)
class GeoJson(Renderable):
    """Base class for adapters which render geojson feature collections.
    """
    extension = 'geojson'
    mimetype = 'application/geojson'
    send_mimetype = 'application/json'

    def featurecollection_properties(self, ctx, req):
        return {}  # pragma: no cover

    def feature_iterator(self, ctx, req):
        return iter([])  # pragma: no cover

    def feature_properties(self, ctx, req, feature):
        return {}  # pragma: no cover

    def feature_coordinates(self, ctx, req, feature):
        """
        :return: lonlat
        """
        return [0.0, 0.0]  # pragma: no cover

    def render(self, ctx, req, dump=True):
        features = []

        for feature in self.feature_iterator(ctx, req):
            properties = self.feature_properties(ctx, req, feature)
            if properties:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": self.feature_coordinates(ctx, req, feature)},
                    "properties": properties,
                })

        res = {
            'type': 'FeatureCollection',
            'properties': self.featurecollection_properties(ctx, req),
            'features': features,
        }
        return pyramid_render('json', res, request=req) if dump else res


class GeoJsonParameter(GeoJson):
    """Render a parameter's values as geojson feature collection.
    """
    def featurecollection_properties(self, ctx, req):
        return {'name': ctx.name}

    def feature_iterator(self, ctx, req):
        return [vs for vs in ctx.valuesets if vs.values]

    def feature_coordinates(self, ctx, req, valueset):
        return [valueset.language.longitude, valueset.language.latitude]

    def feature_properties(self, ctx, req, valueset):
        marker = req.registry.queryUtility(interfaces.IMapMarker)
        _d = {'language': valueset.language.__json__(req)}
        if marker:
            _d['icon'] = marker(valueset, req)
        for i, v in enumerate(valueset.values):
            _d['values_%s' % i] = v.__json__(req)
        return flatten_dict(_d)


@implementer(interfaces.IIndex)
class GeoJsonLanguages(GeoJson):
    """Render a collection of languages as geojson feature collection.
    """
    def feature_iterator(self, ctx, req):
        return ctx.get_query(limit=5000)

    def feature_coordinates(self, ctx, req, feature):
        return [feature.longitude, feature.latitude]

    def feature_properties(self, ctx, req, feature):
        return flatten_dict({'language': feature.__json__(req)})


def includeme(config):
    """register adapters
    """
    specs = []
    for name, interface in [
        ('language', interfaces.ILanguage),
        ('value', interfaces.IValue),
        ('valueset', interfaces.IValueSet),
        ('contribution', interfaces.IContribution),
        ('contributor', interfaces.IContributor),
        ('parameter', interfaces.IParameter),
        ('sentence', interfaces.ISentence),
        ('source', interfaces.ISource),
        ('unit', interfaces.IUnit),
        ('unitparameter', interfaces.IUnitParameter),
    ]:
        specs.append((interface, Index, 'text/html', 'html', name + '/index_html.mako', {}))
        specs.append((interface, Index, 'application/xml', 'sitemap.xml', 'sitemap.mako', {}))
        specs.append((interface, Representation, 'text/html', 'html', name + '/detail_html.mako', {}))
        specs.append((interface, Representation, 'application/vnd.clld.snippet+xml', 'snippet.html', name + '/snippet_html.mako', {}))

    specs.append((interfaces.IContribution, Representation, 'application/vnd.clld.md+xml', 'md.html', 'contribution/md_html.mako', {}))

    specs.extend([
        (interfaces.ILanguage, Index, 'application/vnd.google-earth.kml+xml', 'kml', 'clld:web/templates/language/kml.mako', {'send_mimetype': 'application/xml'}),
        (interfaces.ILanguage, Representation, 'application/rdf+xml', 'rdf', 'clld:web/templates/language/rdf.pt', {}),
        (interfaces.ILanguage, Representation, 'application/vnd.google-earth.kml+xml', 'kml', 'clld:web/templates/language/kml.pt', {'send_mimetype': 'application/xml'}),
        (interfaces.IContribution, Index, 'text/html', 'html', 'contribution/index_html.mako', {}),
    ])

    for i, spec in enumerate(specs):
        interface, base, mimetype, extension, template, extra = spec
        extra.update(mimetype=mimetype, extension=extension, template=template)
        cls = type('Renderer%s' % i, (base,), extra)
        config.registry.registerAdapter(cls, (interface,), list(implementedBy(base))[0], name=mimetype)

    config.registry.registerAdapter(BibTex, (interfaces.IContribution,), interfaces.IRepresentation, name=BibTex.mimetype)
    config.registry.registerAdapter(TxtCitation, (interfaces.IContribution,), interfaces.IRepresentation, name=TxtCitation.mimetype)

    config.registry.registerAdapter(GeoJsonLanguages, (interfaces.ILanguage,), interfaces.IIndex, name=GeoJson.mimetype)
    config.registry.registerAdapter(GeoJsonParameter, (interfaces.IParameter,), interfaces.IRepresentation, name=GeoJson.mimetype)


def get_adapter(interface, ctx, req, ext=None, name=None):
    """
    """
    # ctx can be a DataTable instance. In this case we create a resource by instantiating
    # the model class associated with the DataTable
    resource = ctx.model() if hasattr(ctx, 'model') else ctx
    adapters = dict(req.registry.getAdapters([resource], interface))

    if ext:
        # find adapter by requested file extension
        adapter = [r for r in adapters.values() if r.extension == ext]
    elif name:
        # or by mime type
        adapter = adapters.get(name)
    else:
        # or by content negotiation
        adapter = adapters.get(req.accept.best_match(adapters.keys()))

    return adapter[0] if isinstance(adapter, list) and adapter else adapter
