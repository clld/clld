"""Adapter registry to be included by pyramid configurator."""
import os

from pyramid.path import AssetResolver

from clld import interfaces
from clld.web.adapters.base import Index, Representation, Json, JsonIndex
from clld.web.adapters.geojson import (
    GeoJson, GeoJsonLanguages, GeoJsonParameter, GeoJsonParameterFlatProperties,
)
from clld.web.adapters import excel
from clld.web.adapters import csv
from clld.web.adapters.md import BibTex, TxtCitation, ReferenceManager
from clld.web.adapters.rdf import Rdf, RdfIndex
from clld.web.adapters import biblio
from clld.lib.rdf import FORMATS as RDF_NOTATIONS


def template_exists(config, relpath):
    asset_resolver = AssetResolver()
    for md in config.registry.settings['mako.directories']:
        asset_descriptor = asset_resolver.resolve('/'.join([md, relpath]))
        if os.path.exists(asset_descriptor.abspath()):
            return True
    return False


def register_resource_adapters(config, rsc):
    name, interface = rsc.name, rsc.interface

    config.register_adapter(
        getattr(excel, rsc.plural.capitalize(), excel.ExcelAdapter), interface)
    cls = type('Json%s' % rsc.model.__name__, (Json,), {})
    config.register_adapter(
        cls, interface, to_=interfaces.IRepresentation, name=Json.mimetype)

    specs = []

    if rsc.with_index:
        specs.append((Index, 'application/atom+xml', 'atom', 'index_atom.mako', {}))
        config.register_adapter(
            getattr(csv, rsc.name.capitalize() + 's', csv.CsvAdapter),
            interface,
            interfaces.IIndex,
            name=csv.CsvAdapter.mimetype)
        config.register_adapter(
            csv.CsvmJsonAdapter,
            interface,
            interfaces.IIndex,
            name=csv.CsvmJsonAdapter.mimetype)
        cls = type('JsonIndex%s' % rsc.model.__name__, (JsonIndex,), {})
        config.register_adapter(
            cls, interface, to_=interfaces.IIndex, name=JsonIndex.mimetype)
        if template_exists(config, name + '/index_html.mako'):
            # ... as html index
            specs.append((Index, 'text/html', 'html', name + '/index_html.mako', {}))

    # ... as RDF in various notations
    rdf_resource_template = name + '/rdf.mako'
    if not template_exists(config, rdf_resource_template):
        rdf_resource_template = 'resource_rdf.mako'

    for notation in RDF_NOTATIONS.values():
        specs.append((
            Rdf,
            notation.mimetype,
            notation.extension,
            rdf_resource_template,
            {'name': 'RDF serialized as %s' % notation.name, 'rdflibname': notation.name},
        ))

    # ... as RDF collection index
    rdf_xml = RDF_NOTATIONS['xml']
    specs.append((
        RdfIndex,
        rdf_xml.mimetype,
        rdf_xml.extension,
        'index_rdf.mako',
        {'rdflibname': rdf_xml.name}))

    if template_exists(config, name + '/detail_html.mako'):
        # ... as html details page
        specs.append(
            (Representation, 'text/html', 'html', name + '/detail_html.mako', {}))
    if template_exists(config, name + '/snippet_html.mako'):
        # ... as html snippet (if the template exists)
        specs.append((
            Representation,
            'application/vnd.clld.snippet+xml',
            'snippet.html',
            name + '/snippet_html.mako',
            {'rel': None}))

    config.register_adapters([[interface] + list(spec) for spec in specs])


def includeme(config):
    """register adapters."""
    specs = []

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

    config.register_adapters(specs)

    for cls in [BibTex, TxtCitation, ReferenceManager]:
        for if_ in [interfaces.IRepresentation, interfaces.IMetadata]:
            for adapts in [interfaces.IContribution, interfaces.IDataset]:
                config.register_adapter(cls, adapts, if_, name=cls.mimetype)

    config.register_adapter(
        GeoJsonLanguages,
        interfaces.ILanguage,
        interfaces.IIndex,
        name=GeoJson.mimetype)
    config.register_adapter(
        GeoJsonParameter,
        interfaces.IParameter,
        name=GeoJson.mimetype)
    config.register_adapter(
        GeoJsonParameterFlatProperties,
        interfaces.IParameter,
        name=GeoJsonParameterFlatProperties.mimetype)
    config.include(biblio)


def get_adapters(interface, ctx, req):
    # ctx can be a DataTable instance. In this case we create a resource by instantiating
    # the model class associated with the DataTable
    resource = ctx.model() if hasattr(ctx, 'model') else ctx
    return req.registry.getAdapters([resource], interface)


def get_adapter(interface, ctx, req, ext=None, name=None, getall=False):
    """Retrieve matching adapter.

    :param interface: Interface class to lookup adapter for.
    """
    adapters = dict(get_adapters(interface, ctx, req))

    if not ext and not name and (
        not req.accept or ('*/*' in str(req.accept) and 'q=' not in str(req.accept))
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
        if not hasattr(req.accept, 'acceptable_offers'):  # pragma: no cover
            # pre WebOb 1.8 (should be dropped once pyramid requires WebOb>=1.8):
            adapter = adapters.get(req.accept.best_match(adapters.keys()))
        else:
            try:
                adapter = adapters.get(req.accept.acceptable_offers(list(adapters.keys()))[0][0])
            except IndexError:
                adapter = None

    res = None
    if isinstance(adapter, list):
        if adapter:
            res = adapter[0]
    else:
        res = adapter
    if getall:
        res = (res, adapters.values())
    return res
