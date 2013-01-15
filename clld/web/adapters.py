from itertools import groupby
try:
    from simplejson import dumps
except ImportError:
    from json import dumps

from zope.interface import implementer, implementedBy
from markupsafe import Markup
from mako.template import Template
from pyramid.response import Response
from pyramid.renderers import render as pyramid_render
from sqlalchemy.orm import object_mapper

from clld import interfaces

#    "xml":    "application/xml"+CHARSET_SUFFIX,
#    'xhtml':  'text/html'+CHARSET_SUFFIX,
#    "georss": "application/rss+xml"+CHARSET_SUFFIX,
#    "rss": "application/rss+xml"+CHARSET_SUFFIX,
#    "atom":   "application/atom+xml"+CHARSET_SUFFIX,
#    "kml":    "application/vnd.google-earth.kml+xml"+CHARSET_SUFFIX,
#    "rdf":    "application/rdf+xml"+CHARSET_SUFFIX,
#    "json":   "application/json",
#    "osd":    "application/opensearchdescription+xml"+CHARSET_SUFFIX,


class Renderable(object):
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
    pass


@implementer(interfaces.IRepresentation)
class GeoJson(object):
    extension = 'geojson'
    mimetype = 'application/geojson'

    def __init__(self, obj):
        self.obj = obj

    def render_to_response(self, ctx, req):
        return Response(self.render(ctx, req), content_type='application/json')

    def render(self, ctx, req):
        features = []
        
        for language, values in groupby(ctx.values, lambda v: v.language):
            properties = self.feature_properties(req, language, list(values))
            if properties:
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [language.longitude, language.latitude]},
                    "properties": properties,
                })
        
        return dumps({
            'type': 'FeatureCollection',
            'properties': {'name': ctx.name},
            'features': features,
        })

    def feature_properties(self, req, language, values):
        return {'name': language.name, 'id': language.id}


@implementer(interfaces.IIndex)
class Index(Renderable):
    pass


def includeme(config):
    specs = []
    for name, interface in [
        ('language', interfaces.ILanguage),
        ('contribution', interfaces.IContribution),
        ('contributor', interfaces.IContributor),
        ('parameter', interfaces.IParameter),
        ('example', interfaces.IExample),
        ('source', interfaces.ISource),
    ]:
        specs.append((interface, Index, 'text/html', 'html', name + '/index_html.mako', {}))
        specs.append((interface, Index, 'application/xml', 'sitemap.xml', 'sitemap.mako', {}))
        specs.append((interface, Representation, 'text/html', 'html', name + '/detail_html.mako', {}))
        specs.append((interface, Representation, 'application/vnd.clld.snippet+xml', 'snippet.html', name + '/snippet_html.mako', {}))

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

    config.registry.registerAdapter(GeoJson, (interfaces.IParameter,), interfaces.IRepresentation, name=GeoJson.mimetype)
