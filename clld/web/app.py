"""
Common functionality of CLLD Apps is cobbled together here.
"""
from functools import partial
from collections import OrderedDict
import re
import importlib
from hashlib import md5

from sqlalchemy import engine_from_config
from sqlalchemy.orm import joinedload_all, joinedload
from sqlalchemy.orm.exc import NoResultFound

from path import path
import transaction
from webob.request import Request as WebobRequest
from zope.interface import implementer, implementedBy
from pyramid.httpexceptions import HTTPNotFound
from pyramid import events
from pyramid.request import Request, reify
from pyramid.response import Response
from pyramid.interfaces import IRoutesMapper
from pyramid.asset import abspath_from_asset_spec
from pyramid.config import Configurator
from purl import URL

import clld
from clld.config import get_config
from clld.db.meta import DBSession, Base
from clld.db.models import common
from clld import Resource, RESOURCES
from clld import interfaces
from clld.web.adapters import get_adapters
from clld.web.adapters import excel
from clld.web.views import index_view, resource_view, _raise, _ping, js, unapi
from clld.web.views.olac import olac, OlacConfig
from clld.web.views.sitemap import robots, sitemapindex, sitemap
from clld.web.subscribers import add_renderer_globals, add_localizer, init_map
from clld.web.datatables.base import DataTable
from clld.web import datatables
from clld.web.maps import Map, ParameterMap, LanguageMap
from clld.web.icon import ICONS, MapMarker
from clld.web import assets


class ClldRequest(Request):
    """Custom Request class
    """
    @reify
    def purl(self):
        """For more convenient URL manipulations, we provide a PURL-variant of the current
        request's URL.
        """
        return URL(self.url)

    @property
    def db(self):
        """We make the db session available as request attribute, so we do not have to
        import it in templates.
        """
        return DBSession

    @reify
    def dataset(self):
        """Properties of the dataset an application serves are used in various places,
        so we want to have a reference to it.
        """
        return self.db.query(common.Dataset).first()

    def get_datatable(self, name, model, **kw):
        dt = self.registry.getUtility(interfaces.IDataTable, name)
        return dt(self, model, **kw)

    def _route(self, obj, rsc, **kw):
        """Determines the name of the canonical route for a resource instance. The
        resource may be specified as object or as mapper class and id.

        :return: pair (route_name, kw) suitable as arguments for the Request.route_url \
        method.
        """
        if rsc is None:
            for _rsc in RESOURCES:
                if _rsc.interface.providedBy(obj):
                    rsc = _rsc
                    break
            assert rsc

        route = rsc.name
        if 'ext' in kw:
            route += '_alt'

        # if rsc is passed explicitely, we allow the object id to be passed in as obj,
        # to make it possible to create resource URLs without having the "real" object.
        kw.setdefault('id', getattr(obj, 'id', obj))
        return route, kw

    def ctx_for_url(self, url):
        """Method to reverse URL generation for resources, i.e. given a URL, tries to
        determine the associated resource.

        :return: model instance or None
        """
        mapper = self.registry.getUtility(IRoutesMapper)
        _path = URL(url).path()
        info = mapper(WebobRequest({'PATH_INFO': _path}))
        if not info['route']:
            # FIXME: hack to cater to deployments under a path prefix
            info = mapper(WebobRequest({'PATH_INFO': re.sub('^\/[a-z]+', '', _path)}))
        if info['route'] and info['match']:
            for rsc in RESOURCES:
                if rsc.name == info['route'].name:
                    return rsc.model.get(info['match']['id'], default=None)

    def resource_url(self, obj, rsc=None, **kw):
        route, kw = self._route(obj, rsc, **kw)
        return self.route_url(route, **kw)

    def resource_path(self, obj, rsc=None, **kw):
        route, kw = self._route(obj, rsc, **kw)
        return self.route_path(route, **kw)

    def file_url(self, file_):
        if 'clld.files' in self.registry.settings:
            abspath = self.registry.settings['clld.files'].joinpath(file_.relpath)
            return self.static_url(abspath)


def menu_item(resource, ctx, req, label=None):
    """
    :return: A pair (URL, label) to create a menu item.
    """
    return req.route_url(resource), label or req.translate(resource.capitalize())


@implementer(interfaces.ICtxFactoryQuery)
class CtxFactoryQuery(object):
    """Implements reasonable default queries to be used in context factories.

    By reasonable we mean providing good performance for typical data sizes. Applications
    with a-typical numbers of any resource class may have to implement a custom class
    for the ICtxFactoryQuery interface. Usually this will be a class derived from
    CtxFactoryQuery.
    """
    def refined_query(self, query, model, req):
        """Derived classes may override this method to add model-specific query
        refinements of their own.
        """
        return query

    def __call__(self, model, req):
        query = req.db.query(model).filter(model.id == req.matchdict['id'])
        custom_query = self.refined_query(query, model, req)

        if query == custom_query:
            # no customizations done, apply the defaults
            if model == common.Contribution:
                query = query.options(
                    joinedload_all(
                        common.Contribution.valuesets,
                        common.ValueSet.parameter,
                    ),
                    joinedload_all(
                        common.Contribution.valuesets,
                        common.ValueSet.values,
                        common.Value.domainelement),
                    joinedload_all(
                        common.Contribution.references,
                        common.ContributionReference.source),
                    joinedload(common.Contribution.data),
                )
            if model == common.ValueSet:
                query = query.options(
                    joinedload(common.ValueSet.values),
                    joinedload(common.ValueSet.parameter),
                    joinedload(common.ValueSet.language),
                )
        else:
            query = custom_query  # pragma: no cover

        return query.one()


def ctx_factory(model, type_, req):
    """The context of a request is either a single model instance or an instance of
    DataTable incorporating all information to retrieve an appropriately filtered list
    of model instances.
    """
    if type_ == 'index':
        datatable = req.registry.getUtility(
            interfaces.IDataTable, name=req.matched_route.name)
        return datatable(req, model)

    try:
        if model == common.Dataset:
            ctx = req.db.query(model).one()
        else:
            ctx = req.registry.getUtility(interfaces.ICtxFactoryQuery)(model, req)
        ctx.metadata = get_adapters(interfaces.IMetadata, ctx, req)
        return ctx
    except NoResultFound:
        raise HTTPNotFound()


def maybe_import(name):
    try:
        return importlib.import_module(name)
    except ImportError:
        return None


#
# configurator directives:
#
def register_cls(interface, config, route, cls):
    config.registry.registerUtility(cls, provided=interface, name=route)
    if not route.endswith('_alt'):
        config.registry.registerUtility(cls, provided=interface, name=route + '_alt')


def register_adapter(config, cls, from_, to_=None, name=None):
    to_ = to_ or list(implementedBy(cls))[0]
    name = name or cls.mimetype
    config.registry.registerAdapter(cls, (from_,), to_, name=name)


def register_menu(config, *items):
    """
    :param factory: a callable that accepts the two parameters (ctx, req) and returns\
    a pair (url, label) to use for the menu link.
    """
    menuitems = OrderedDict()
    for name, factory in items:
        menuitems[name] = factory
    config.registry.registerUtility(menuitems, interfaces.IMenuItems)


def add_route_and_view(config, route_name, route_pattern, view, **kw):
    """
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


def register_resource(config, name, model, interface, with_index=False):
    # in case of tests, this method may be called multiple times!
    if [rsc for rsc in RESOURCES if rsc.name == name]:
        return
    RESOURCES.append(Resource(name, model, interface, with_index=with_index))
    config.register_adapter(excel.ExcelAdapter, interface)
    config.add_route_and_view(
        name,
        '/%ss/{id:[^/\.]+}' % name,
        resource_view,
        factory=partial(ctx_factory, model, 'rsc'))
    if with_index:
        config.add_route_and_view(
            name + 's',
            '/%ss' % name,
            index_view,
            factory=partial(ctx_factory, model, 'index'))


def register_download(config, download):
    config.registry.registerUtility(download, interfaces.IDownload, name=download.name)


def get_configurator(pkg, *utilities, **kw):
    """
    .. seealso:: https://groups.google.com/d/msg/pylons-discuss/Od6qIGaLV6A/3mXVBQ13zWQJ
    """
    kw.setdefault('package', pkg)
    routes = kw.pop('routes', [])

    config = Configurator(**kw)

    for name, pattern in routes:
        config.add_route(name, pattern)

    config.set_request_factory(ClldRequest)
    config.registry.registerUtility(CtxFactoryQuery(), interfaces.ICtxFactoryQuery)
    config.registry.registerUtility(OlacConfig(), interfaces.IOlacConfig)

    # initialize the db connection
    engine = engine_from_config(config.registry.settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config.add_settings({'pyramid.default_locale_name': 'en'})
    if 'clld.files' in config.registry.settings:
        abspath = path(config.registry.settings['clld.files']).abspath()
        config.add_settings({'clld.files': abspath})
        config.add_static_view('files', abspath)

    # event subscribers:
    config.add_subscriber(add_localizer, events.NewRequest)
    config.add_subscriber(init_map, events.ContextFound)
    config.add_subscriber(
        partial(add_renderer_globals, maybe_import('%s.util' % config.package_name)),
        events.BeforeRender)

    #
    # make it easy to register custom functionality
    #
    for name, func in {
        'register_datatable': partial(register_cls, interfaces.IDataTable),
        'register_map': partial(register_cls, interfaces.IMap),
        'register_menu': register_menu,
        'register_resource': register_resource,
        'register_adapter': register_adapter,
        'register_download': register_download,
        'add_route_and_view': add_route_and_view,
    }.items():
        config.add_directive(name, func)

    #
    # routes and views
    #
    config.add_static_view('clld-static', 'clld:web/static')
    config.add_static_view('static', '%s:static' % config.package_name)

    config.add_route_and_view('legal', '/legal', lambda r: {}, renderer='legal.mako')
    config.add_route_and_view('download', '/download', lambda r: {}, renderer='download.mako')
    config.add_route_and_view('contact', '/contact', lambda r: {}, renderer='contact.mako')
    config.add_route_and_view('_js', '/_js', js, http_cache=3600)

    # add some maintenance hatches
    config.add_route_and_view('_raise', '/_raise', _raise)
    config.add_route_and_view('_ping', '/_ping', _ping, renderer='json')

    # sitemap support:
    config.add_route_and_view('robots', '/robots.txt', robots)
    config.add_route_and_view('sitemapindex', '/sitemap.xml', sitemapindex)
    config.add_route_and_view('sitemap', '/sitemap.{rsc}.{n}.xml', sitemap)

    config.add_route('google-site-verification', 'googlebbc8f4da1abdc58b.html')
    config.add_view(
        lambda r: Response('google-site-verification: googlebbc8f4da1abdc58b.html'),
        route_name='google-site-verification')

    config.add_route_and_view('unapi', '/unapi', unapi)
    config.add_route_and_view('olac', '/olac', olac)

    for rsc in RESOURCES:
        name, model = rsc.name, rsc.model
        factory = partial(ctx_factory, model, 'index')
        config.add_route_and_view(rsc.plural, '/%s' % rsc.plural, index_view, factory=factory)
        config.register_datatable(
            rsc.plural, getattr(datatables, rsc.plural.capitalize(), DataTable))
        config.register_adapter(
            getattr(excel, rsc.plural.capitalize(), excel.ExcelAdapter), rsc.interface)

        kw = dict(factory=partial(ctx_factory, model, 'rsc'))
        if model == common.Dataset:
            pattern = '/'
            kw['alt_route_pattern'] = '/void.{ext}'
        else:
            pattern = '/%s/{id:[^/\.]+}' % rsc.plural

        config.add_route_and_view(name, pattern, resource_view, **kw)

    # maps
    config.register_map('languages', Map)
    config.register_map('language', LanguageMap)
    config.register_map('parameter', ParameterMap)

    config.include('clld.web.adapters')

    for icon in ICONS:
        config.registry.registerUtility(icon, interfaces.IIcon, name=icon.name)
    config.registry.registerUtility(MapMarker(), interfaces.IMapMarker)

    #
    # now we exploit the default package layout as created via the CLLD scaffold:
    #
    # note: the following exploits the import time side effect of modifying the webassets
    # environment!
    maybe_import('%s.assets' % config.package_name)

    pkg_dir = path(config.package.__file__).dirname().abspath()

    if 'clld.favicon' not in config.registry.settings:
        favicon = {'clld.favicon': 'clld:web/static/images/favicon.ico'}
        if pkg_dir.joinpath('static', 'favicon.ico').exists():
            favicon['clld.favicon'] = config.package_name + ':static/favicon.ico'
        config.add_settings(favicon)

    with open(abspath_from_asset_spec(config.registry.settings['clld.favicon'])) as fp:
        fh = md5()
        fh.update(fp.read())
        config.add_settings({'clld.favicon_hash': fh.hexdigest()})

    if pkg_dir.joinpath('locale').exists():
        config.add_translation_dirs('%s:locale' % config.package_name)
        config.add_translation_dirs('clld:locale')

    if pkg_dir.joinpath('appconf.ini').exists():
        cfg = get_config(pkg_dir.joinpath('appconf.ini'))
        if 'mako.directories_list' in cfg:
            cfg['mako.directories'] = cfg['mako.directories_list']  # pragma: no cover
        config.add_settings(cfg)

    v = maybe_import('%s.views' % config.package_name)
    if v:
        config.scan(v)  # pragma: no cover

    menuitems = OrderedDict(dataset=partial(menu_item, 'dataset', label='home'))
    for plural in config.registry.settings.get(
        'clld.menuitems_list',
        ['contributions', 'parameters', 'languages', 'contributors']
    ):
        menuitems[plural] = partial(menu_item, plural)
    config.registry.registerUtility(menuitems, interfaces.IMenuItems)

    for utility, interface in utilities:
        config.registry.registerUtility(utility, interface)
    return config
