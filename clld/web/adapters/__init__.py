from zope.interface import implementedBy

from clld import RESOURCES
from clld import interfaces
from clld.web.adapters.base import Index, Representation, Json, SolrDoc
from clld.web.adapters.geojson import (
    GeoJson, GeoJsonLanguages, GeoJsonParameter, GeoJsonParameterFlatProperties,
)
from clld.web.adapters.excel import ExcelAdapter
assert ExcelAdapter
from clld.web.adapters.md import BibTex, TxtCitation, ReferenceManager
from clld.web.adapters.rdf import Rdf, RdfIndex
from clld.web.adapters import biblio
from clld.lib.rdf import FORMATS as RDF_NOTATIONS


def includeme(config):
    """register adapters
    """
    specs = []
    for rsc in RESOURCES:
        # each resource is available ...
        name, interface = rsc.name, rsc.interface

        # ... as json
        cls = type('Json%s' % rsc.model.mapper_name(), (Json,), {})
        config.registry.registerAdapter(
            cls, (interface,), interfaces.IRepresentation, name=Json.mimetype)
        cls = type('Solr%s' % rsc.model.mapper_name(), (SolrDoc,), {})
        config.registry.registerAdapter(
            cls, (interface,), interfaces.IRepresentation, name=SolrDoc.mimetype)

        if rsc.with_index:
            # ... as html index
            specs.append(
                (interface, Index, 'text/html', 'html', name + '/index_html.mako', {}))
            specs.append(
                (interface, Index, 'application/atom+xml', 'atom', 'index_atom.mako', {}))

        # ... as html details page
        specs.append(
            (interface, Representation, 'text/html', 'html', name + '/detail_html.mako',
             {}))
        # ... as html snippet (if the template exists)
        specs.append(
            (interface, Representation, 'application/vnd.clld.snippet+xml',
             'snippet.html', name + '/snippet_html.mako', {'rel': None}))

        # ... as RDF in various notations
        for notation in RDF_NOTATIONS.values():
            specs.append((
                interface,
                Rdf,
                notation.mimetype,
                notation.extension,
                name + '/rdf.mako',
                {
                    'name': 'RDF serialized as %s' % notation.name,
                    'rdflibname': notation.name}))

        # ... as RDF collection index
        rdf_xml = RDF_NOTATIONS['xml']
        specs.append((
            interface,
            RdfIndex,
            rdf_xml.mimetype,
            rdf_xml.extension,
            'index_rdf.mako', {'rdflibname': rdf_xml.name}))

    # citeable resources are available as html page listing available metadata formats:
    for _if in [interfaces.IContribution, interfaces.IDataset]:
        specs.append((
            _if,
            Representation,
            'application/vnd.clld.md+xml',
            'md.html',
            'md_html.mako',
            {'rel': 'describedby'}))

    specs.append((
        interfaces.ILanguage, Index,
        'application/vnd.google-earth.kml+xml',
        'kml',
        'clld:web/templates/language/kml.mako',
        {'send_mimetype': 'application/xml'}))

    for i, spec in enumerate(specs):
        interface, base, mimetype, extension, template, extra = spec
        extra.update(mimetype=mimetype, extension=extension, template=template)
        cls = type('Renderer%s' % i, (base,), extra)
        config.registry.registerAdapter(
            cls, (interface,), list(implementedBy(base))[0], name=mimetype)

    for cls in [BibTex, TxtCitation, ReferenceManager]:
        for if_ in [interfaces.IRepresentation, interfaces.IMetadata]:
            for adapts in [interfaces.IContribution, interfaces.IDataset]:
                config.registry.registerAdapter(
                    cls,
                    (adapts,),
                    if_,
                    name=cls.mimetype)

    config.registry.registerAdapter(
        GeoJsonLanguages,
        (interfaces.ILanguage,),
        interfaces.IIndex,
        name=GeoJson.mimetype)
    config.registry.registerAdapter(
        GeoJsonParameter,
        (interfaces.IParameter,),
        interfaces.IRepresentation,
        name=GeoJson.mimetype)
    config.registry.registerAdapter(
        GeoJsonParameterFlatProperties,
        (interfaces.IParameter,),
        interfaces.IRepresentation,
        name=GeoJsonParameterFlatProperties.mimetype)

    config.include(biblio)


def get_adapters(interface, ctx, req):
    # ctx can be a DataTable instance. In this case we create a resource by instantiating
    # the model class associated with the DataTable
    resource = ctx.model() if hasattr(ctx, 'model') else ctx
    return req.registry.getAdapters([resource], interface)


def get_adapter(interface, ctx, req, ext=None, name=None, getall=False):
    """
    """
    adapters = dict(get_adapters(interface, ctx, req))

    if not ext and not name and (
        not req.accept or ('*/*' in str(req.accept) and not 'q=' in str(req.accept))
    ):
        # force text/html in case there are no specific criteria to decide
        # or we suspect some weird IE accept header.
        # see also http://www.gethifi.com/blog/browser-rest-http-accept-headers
        ext = 'html'

    if ext:
        # find adapter by requested file extension
        adapter = [r for r in adapters.values() if r.extension == ext]
    elif name:
        # or by mime type
        adapter = adapters.get(name)
    else:
        # or by content negotiation
        #
        # TODO: iterate over req.accept (i.e. over the accepted mimetypes in order of
        # preference) and match them to what we have to offer (in order of preference).
        #
        adapter = adapters.get(req.accept.best_match(adapters.keys()))

    res = None
    if isinstance(adapter, list):
        if adapter:
            res = adapter[0]
    else:
        res = adapter
    if getall:
        res = (res, adapters.values())
    return res
