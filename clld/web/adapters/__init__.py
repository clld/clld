from zope.interface import implementer, implementedBy

from clld import RESOURCES
from clld import interfaces
from clld.web.adapters.base import Index, Representation, OctetStream, Json
from clld.web.adapters.geojson import GeoJson, GeoJsonLanguages, GeoJsonParameter
from clld.web.adapters.excel import ExcelAdapter
from clld.web.adapters.md import BibTex, TxtCitation
from clld.web.adapters.rdf import Rdf
from clld.web.adapters import biblio
from clld.lib.rdf import FORMATS as RDF_NOTATIONS


def includeme(config):
    """register adapters
    """
    specs = []
    for rsc in RESOURCES:
        name, interface = rsc.name, rsc.interface

        if not rsc.with_adapters:
            continue

        cls = type('Json%s' % rsc.model.mapper_name(), (Json,), {})
        config.registry.registerAdapter(
            cls, (interface,), interfaces.IRepresentation, name=Json.mimetype)

        if rsc.with_index:
            specs.append(
                (interface, Index, 'text/html', 'html', name + '/index_html.mako', {}))

        specs.append(
            (interface, Representation, 'text/html', 'html', name + '/detail_html.mako',
             {}))
        specs.append(
            (interface, Representation, 'application/vnd.clld.snippet+xml',
             'snippet.html', name + '/snippet_html.mako', {}))
        for notation in RDF_NOTATIONS.values():
            specs.append((
                interface,
                Rdf,
                notation.mimetype,
                notation.extension,
                name + '/rdf.mako', {'rdflibname': notation.name}))

    specs.append(
        (interfaces.IContribution, Representation, 'application/vnd.clld.md+xml',
         'md.html', 'contribution/md_html.mako', {}))

    specs.extend([
        (
            interfaces.ILanguage, Index,
            'application/vnd.google-earth.kml+xml',
            'kml',
            'clld:web/templates/language/kml.mako',
            {'send_mimetype': 'application/xml'}),
        (
            interfaces.ILanguage,
            Representation,
            'application/vnd.google-earth.kml+xml',
            'kml',
            'clld:web/templates/language/kml.pt',
            {'send_mimetype': 'application/xml'}),
        (
            interfaces.IContribution,
            Index,
            'text/html',
            'html',
            'contribution/index_html.mako',
            {}),
    ])

    for i, spec in enumerate(specs):
        interface, base, mimetype, extension, template, extra = spec
        extra.update(mimetype=mimetype, extension=extension, template=template)
        cls = type('Renderer%s' % i, (base,), extra)
        config.registry.registerAdapter(
            cls, (interface,), list(implementedBy(base))[0], name=mimetype)

    for cls in [BibTex, TxtCitation]:
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
        OctetStream,
        (interfaces.IFile,),
        interfaces.IRepresentation,
        name=OctetStream.mimetype)

    config.include(biblio)


def get_adapters(interface, ctx, req):
    # ctx can be a DataTable instance. In this case we create a resource by instantiating
    # the model class associated with the DataTable
    resource = ctx.model() if hasattr(ctx, 'model') else ctx
    return req.registry.getAdapters([resource], interface)


def get_adapter(interface, ctx, req, ext=None, name=None):
    """
    """
    adapters = dict(get_adapters(interface, ctx, req))

    if ext:
        # find adapter by requested file extension
        adapter = [r for r in adapters.values() if r.extension == ext]
    elif name:
        # or by mime type
        adapter = adapters.get(name)
    else:
        # or by content negotiation
        adapter = adapters.get(req.accept.best_match(adapters.keys()))

    if isinstance(adapter, list):
        if adapter:
            return adapter[0]
        return None
    return adapter
