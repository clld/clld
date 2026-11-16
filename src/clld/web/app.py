"""Common functionality of clld Apps is cobbled together here."""
import uuid
import pathlib
import datetime
import functools
import importlib
import collections

from sqlalchemy import engine_from_config
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound

from zope.interface import implementer, implementedBy
from pyramid.httpexceptions import HTTPNotFound, HTTPMovedPermanently, HTTPGone
from pyramid import events
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.asset import abspath_from_asset_spec
from pyramid.renderers import JSON, JSONP
from pyramid.settings import asbool
from clldutils.path import md5, git_describe

import clld
from clld.config import get_config
from clld.db.meta import DBSession, Base
from clld.db.models import common
from clld import Resource, RESOURCES
from clld import interfaces
from clld.web.adapters import get_adapters
from clld.web.adapters import geojson, register_resource_adapters
from clld.web.adapters.base import adapter_factory
from clld.web.views import (
    index_view, resource_view, _raise, _ping, js, unapi, xpartial, redirect, gone,
    select_combination,
)
from clld.web import assets
from clld.web.views.olac import olac, OlacConfig
from clld.web.views.sitemap import robots, sitemapindex, sitemap, resourcemap
from clld.web.subscribers import add_renderer_globals, add_localizer, init_map
from clld.web.datatables.base import DataTable
from clld.web import datatables
from clld.web.maps import Map, ParameterMap, LanguageMap, CombinationMap
from clld.web.icon import ICONS, MapMarker
from clld.web.request import ClldRequest

assert clld
assert assets


def menu_item(route_name: str, ctx, req: Request, label: str | None = None):
    """Factory function for a menu item specified by route name.

    :return: A pair (URL, label) to create a menu item.
    """
    return req.route_url(route_name), label or req.translate(route_name.capitalize())


@implementer(interfaces.ICtxFactoryQuery)
class CtxFactoryQuery:

    """Implements reasonable default queries to be used in context factories.

    By reasonable we mean providing good performance for typical data sizes. Applications
    with a-typical numbers of any resource class may have to implement a custom class
    for the ICtxFactoryQuery interface. Usually this will be a class derived from
    CtxFactoryQuery.
    """

    def refined_query(self, query, model, req: Request):
        """To be overridden.

        Derived classes may override this method to add model-specific query
        refinements of their own.
        """
        return query

    def __call__(self, model, req: Request):
        query = req.db.query(model).filter(model.id == req.matchdict['id'])
        custom_query = self.refined_query(query, model, req)

        if query == custom_query:
            # no customizations done, apply the defaults
            f = getattr(model, 'refine_factory_query', None)
            if f:
                query = f(query)
            elif model == common.Contribution:
                query = query.options(
                    joinedload(common.Contribution.valuesets
                    ).joinedload(common.ValueSet.parameter
                    ),
                    joinedload(common.Contribution.valuesets
                    ).joinedload(common.ValueSet.values
                    ).joinedload(common.Value.domainelement
                    ),
                    joinedload(common.Contribution.references
                    ).joinedload(common.ContributionReference.source),
                    joinedload(common.Contribution.data)
                )
        else:
            query = custom_query  # pragma: no cover

        return query.one()


def ctx_factory(model, type_, req):
    """Factory function for request contexts.

    The context of a request is either a single model instance or an instance of
    DataTable incorporating all information to retrieve an appropriately filtered list
    of model instances.
    """
    def replacement(id_):
        raise HTTPMovedPermanently(
            location=req.route_url(model.__name__.lower(), id=id_))

    if type_ == 'index':
        datatable = req.registry.getUtility(
            interfaces.IDataTable, name=req.matched_route.name)
        return datatable(req, model)

    try:
        if model == common.Dataset:
            ctx = req.db.query(model).one()
        elif model == common.Combination:
            ctx = common.Combination.get(req.matchdict['id'])
        else:
            ctx = req.registry.getUtility(interfaces.ICtxFactoryQuery)(model, req)
            if ctx.replacement_id:
                return replacement(ctx.replacement_id)
        ctx.metadata = get_adapters(interfaces.IMetadata, ctx, req)
        return ctx
    except NoResultFound:
        if req.matchdict.get('id'):
            replacement_id = common.Config.get_replacement_id(model, req.matchdict['id'])
            if replacement_id:
                if replacement_id == common.Config.gone:
                    raise HTTPGone()
                return replacement(replacement_id)
        raise HTTPNotFound()


def maybe_import(name, pkg_dir=None):
    exists = False
    if pkg_dir:
        rel_path = name.split('.')[1:] if '.' in name else []
        rel_path.append('__init__.py')
        exists = pkg_dir.joinpath(*rel_path).exists()
        if not exists:
            rel_path.pop()
            if rel_path:
                rel_path[-1] += '.py'
            exists = pkg_dir.joinpath(*rel_path).exists()
    try:
        return importlib.import_module(name)
    except ImportError:
        if pkg_dir and exists:
            print(f'failed to import existing module {name}')
            raise


#
# configurator directives:
#
def register_utility(config: Configurator, cls, interface, name='', overwrite=True):
    if overwrite or not config.registry.queryUtility(interface, name=name):
        config.registry.registerUtility(cls, provided=interface, name=name)


def register_cls(interface, config: Configurator, route: str, cls, overwrite=True):
    register_utility(config, cls, interface, name=route, overwrite=overwrite)
    if not route.endswith('_alt'):
        register_utility(config, cls, interface, name=route + '_alt', overwrite=overwrite)


def register_adapter(config: Configurator, cls, from_, to_=None, name=None):
    if isinstance(cls, dict):
        cls = adapter_factory(**cls)
    to_ = to_ or list(implementedBy(cls))[0]
    name = name or cls.mimetype
    config.registry.registerAdapter(cls, (from_,), to_, name=name)


def register_adapters(config: Configurator, specs):
    for interface, base, mimetype, extension, template, extra in specs:
        extra.update(base=base, mimetype=mimetype, extension=extension, template=template)
        config.register_adapter(extra, interface, name=mimetype)


def register_menu(config: Configurator, *items):
    """Register an item for the main menu.

    :param items: An item may be a (name, factory) pair, where factory is a callable that\
    accepts the two parameters (ctx, req) and returns a pair (url, label) to use for the\
    menu link; or a route name, or a pair (route name, dict), where dict is used as\
    keyword arguments for menu_item.
    """
    menuitems = collections.OrderedDict()
    for item in items:
        if isinstance(item, str):
            item = (item, {})
        name, factory = item
        if isinstance(factory, dict):
            factory = functools.partial(menu_item, name, **factory)
        menuitems[name] = factory
    config.registry.registerUtility(menuitems, interfaces.IMenuItems)


def add_route_and_view(config: Configurator, route_name, route_pattern, view, **kw):
    """Add a route and a corresponding view and appropriate default routes and views.

    .. note:: To allow custom route patterns we look them up in a dict in settings.
    """
    route_patterns = config.registry.settings.get('route_patterns', {})
    route_pattern = route_patterns.get(route_name, route_pattern)
    alt_route_pattern = kw.pop('alt_route_pattern', route_pattern + '.{ext}')
    route_kw = {}
    factory = kw.pop('factory', None)
    if factory:
        route_kw['factory'] = factory
    config.add_route(route_name, route_pattern, **route_kw)
    config.add_view(view, route_name=route_name, **kw)

    config.add_route(route_name + '_alt', alt_route_pattern, **route_kw)
    config.add_view(view, route_name=route_name + '_alt', **kw)


def register_resource_routes_and_views(config: Configurator, rsc):
    kw = dict(factory=functools.partial(ctx_factory, rsc.model, 'rsc'))
    if rsc.model == common.Dataset:
        pattern = '/'
        kw['alt_route_pattern'] = '/void.{ext}'
    else:
        pattern = r'/%s/{id:[^/\.]+}' % rsc.plural

    config.add_route_and_view(rsc.name, pattern, resource_view, **kw)
    if rsc.with_index:
        config.add_route_and_view(
            rsc.plural,
            '/%s' % rsc.plural,
            index_view,
            factory=functools.partial(ctx_factory, rsc.model, 'index'))


def register_resource(config: Configurator, name, model, interface, with_index=False, **kw):
    """Directive to register custom resources.

    .. note::

        The directive accepts arbitrary keyword arguments for backwards compatibility.
    """
    # in case of tests, this method may be called multiple times!
    if [rsc for rsc in RESOURCES if rsc.name == name]:
        return
    rsc = Resource(name, model, interface, with_index=with_index)
    RESOURCES.append(rsc)
    config.register_resource_routes_and_views(rsc)

    if not config.registry.queryUtility(interfaces.IDataTable, name=rsc.plural):
        config.register_datatable(
            rsc.plural, getattr(datatables, rsc.plural.capitalize(), DataTable))

    register_resource_adapters(config, rsc)


def register_download(config: Configurator, download):
    config.registry.registerUtility(download, interfaces.IDownload, name=download.name)


StaticResource = collections.namedtuple('StaticResource', 'type asset_spec')


def register_staticresource(config: Configurator, type, asset_spec):
    config.registry.registerUtility(
        StaticResource(type, asset_spec), interfaces.IStaticResource, name=asset_spec)


def add_settings_from_file(config, file_):
    if file_.exists():
        cfg = get_config(file_)
        if 'mako.directories_list' in cfg:
            cfg['mako.directories'] = cfg['mako.directories_list']  # pragma: no cover
        config.add_settings(cfg)


def _route_and_view(config: Configurator, pattern, view, name=None):
    name = name or str(uuid.uuid4())
    config.add_route(name, pattern)
    config.add_view(view, route_name=name)


def add_301(config: Configurator, pattern, location, name=None):
    _route_and_view(
        config, pattern, xpartial(redirect, HTTPMovedPermanently, location), name=name)


def add_410(config: Configurator, pattern, name=None):
    _route_and_view(config, pattern, gone, name=name)


def add_page(  # noqa: PLR0917,PLR0913
        config: Configurator, name: str, pattern=None, view=None, template=None, views=None):
    views = views or maybe_import(f'{config.root_package.__name__}.views')
    config.add_route_and_view(
        name,
        pattern or '/' + name,
        view or getattr(views, name, lambda r: {}),
        renderer=template or name + '.mako')


def includeme(config: Configurator):  # noqa: PLR0915,PLR0912,C901
    """Upgrading:

    - register utilities "by hand", after config.include('clld.web.app')
    - add routes by hand (and remove these from the **kw passed to Configurator)

    :param config:
    :return:
    """
    #
    # now we exploit the default package layout as created via the CLLD scaffold:
    #
    # note: the following exploits the import time side effect of modifying the webassets
    # environment!
    root_package = config.root_package.__name__
    pkg_dir = pathlib.Path(config.root_package.__file__).parent.resolve()
    maybe_import('%s.assets' % root_package, pkg_dir=pkg_dir)

    json_renderer = JSON()
    json_renderer.add_adapter(datetime.datetime, lambda obj, req: obj.isoformat())
    json_renderer.add_adapter(datetime.date, lambda obj, req: obj.isoformat())
    config.add_renderer('json', json_renderer)

    jsonp_renderer = JSONP(param_name='callback')
    jsonp_renderer.add_adapter(datetime.datetime, lambda obj, req: obj.isoformat())
    jsonp_renderer.add_adapter(datetime.date, lambda obj, req: obj.isoformat())
    config.add_renderer('jsonp', jsonp_renderer)

    config.set_request_factory(ClldRequest)
    config.registry.registerUtility(CtxFactoryQuery(), interfaces.ICtxFactoryQuery)
    config.registry.registerUtility(OlacConfig(), interfaces.IOlacConfig)

    # initialize the db connection
    if not DBSession.registry.has():
        engine = engine_from_config(config.registry.settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

    try:
        git_tag = git_describe(pathlib.Path(pkg_dir).parent)
    except ValueError:  # pragma: no cover
        git_tag = None

    config.add_settings({
        'pyramid.default_locale_name': 'en',
        'clld.pkg': root_package,
        'clld.git_tag': git_tag,
        'clld.parameters': {}})
    if 'clld.files' in config.registry.settings:
        # deployment-specific location of static data files
        abspath = pathlib.Path(config.registry.settings['clld.files']).resolve()
        config.add_settings({'clld.files': abspath})
        config.add_static_view('files', str(abspath))

    # event subscribers:
    config.add_subscriber(add_localizer, events.NewRequest)
    config.add_subscriber(init_map, events.ContextFound)
    config.add_subscriber(
        functools.partial(
            add_renderer_globals,
            maybe_import('%s.util' % root_package, pkg_dir=pkg_dir)),
        events.BeforeRender)

    #
    # make it easy to register custom functionality
    #
    for name, func in {
        'register_utility': register_utility,
        'register_datatable': functools.partial(register_cls, interfaces.IDataTable),
        'register_map': functools.partial(register_cls, interfaces.IMap),
        'register_menu': register_menu,
        'register_resource': register_resource,
        'register_adapter': register_adapter,
        'register_adapters': register_adapters,
        'register_download': register_download,
        'register_staticresource': register_staticresource,
        'add_route_and_view': add_route_and_view,
        'add_settings_from_file': add_settings_from_file,
        'add_301': add_301,
        'add_410': add_410,
        'add_page': add_page,
        'register_resource_routes_and_views': register_resource_routes_and_views,
    }.items():
        config.add_directive(name, func)

    #
    # routes and views
    #
    config.add_static_view('clld-static', 'clld:web/static')
    config.add_static_view('static', '%s:static' % root_package)

    config.add_route_and_view('_js', '/_js', js, http_cache=3600)

    # add some maintenance hatches
    config.add_route_and_view('_raise', '/_raise', _raise)
    config.add_route_and_view('_ping', '/_ping', _ping, renderer='json')

    # sitemap support:
    config.add_route_and_view('robots', '/robots.txt', robots)
    config.add_route_and_view('sitemapindex', '/sitemap.xml', sitemapindex)
    config.add_route_and_view('sitemap', '/sitemap.{rsc}.{n}.xml', sitemap)
    config.add_route('resourcemap', '/resourcemap.json')
    config.add_view(resourcemap, route_name='resourcemap', renderer='jsonp')
    config.add_route_and_view(
        'select_combination', '/_select_combination', select_combination)

    config.add_route_and_view('unapi', '/unapi', unapi)
    config.add_route_and_view('olac', '/olac', olac)

    config.add_settings_from_file(pkg_dir.joinpath('appconf.ini'))
    if not config.registry.settings.get('mako.directories'):
        config.add_settings({'mako.directories': ['clld:web/templates']})

    for rsc in RESOURCES:
        config.register_resource_routes_and_views(rsc)
        config.register_datatable(
            rsc.plural, getattr(datatables, rsc.plural.capitalize(), DataTable))
        register_resource_adapters(config, rsc)

    # maps
    config.register_map('languages', Map)
    config.register_map('language', LanguageMap)
    config.register_map('parameter', ParameterMap)
    config.register_map('combination', CombinationMap)

    config.include('clld.web.adapters')

    for icon in ICONS:
        config.registry.registerUtility(icon, interfaces.IIcon, name=icon.name)
    config.registry.registerUtility(MapMarker(), interfaces.IMapMarker)

    #
    # inspect default locations for views and templates:
    #
    home_comp = collections.OrderedDict()
    for name, template in [
        ('introduction', False),
        ('about', False),
        ('terms', False),
        ('glossary', False),
        ('history', False),
        ('changes', False),
        ('credits', False),
        ('legal', True),
        ('download', True),
        ('contact', True),
        ('help', False),
    ]:
        home_comp[name] = template

    if pkg_dir.joinpath('templates').exists():
        for p in pkg_dir.joinpath('templates').iterdir():
            if p.stem in home_comp and p.suffix == '.mako':
                home_comp[p.stem] = True

    for name, template in home_comp.items():
        if template:
            config.add_page(name)

    config.add_settings({'home_comp': [k for k in home_comp.keys() if home_comp[k]]})

    if 'clld.favicon' not in config.registry.settings:
        favicon = {'clld.favicon': 'clld:web/static/images/favicon.ico'}
        # hard to test (in particular on travis) and without too much consequence
        # (and the consequences faced are easy to spot).
        if pkg_dir.joinpath('static', 'favicon.ico').exists():  # pragma: no cover
            favicon['clld.favicon'] = root_package + ':static/favicon.ico'
        config.add_settings(favicon)

    config.add_settings({
        'clld.favicon_hash': md5(abspath_from_asset_spec(
            config.registry.settings['clld.favicon']))})

    translation_dirs = ['clld:locale']
    if pkg_dir.joinpath('locale').exists():
        translation_dirs.append('%s:locale' % root_package)  # pragma: no cover
    config.add_translation_dirs(*translation_dirs)

    if pkg_dir.joinpath('static/publisher_logo.png').exists():  # pragma: no cover
        config.add_settings(
            {'clld.publisher_logo': '%s:static/publisher_logo.png' % root_package})

    if asbool(config.registry.settings.get('clld.pacific_centered_maps')):
        geojson.pacific_centered()

    v = maybe_import('%s.views' % root_package, pkg_dir=pkg_dir)
    if v:
        config.scan(v)  # pragma: no cover

    menuitems = config.registry.settings.get(
        'clld.menuitems_list',
        ['contributions', 'parameters', 'languages', 'contributors'])
    config.register_menu(
        ('dataset', lambda ctx, req: (req.resource_url(req.dataset), req.translate('Home'))),
        *menuitems)

    config.include('pyramid_mako')

    for name in ['adapters', 'datatables', 'maps']:
        mod = maybe_import('%s.%s' % (root_package, name), pkg_dir=pkg_dir)
        if mod and hasattr(mod, 'includeme'):
            config.include(mod)
