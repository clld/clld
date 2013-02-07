"""
Common functionality of CLLD Apps is cobbled together here.
"""
from functools import partial
from collections import OrderedDict

from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from path import path

from zope.interface import implementer, implementedBy
from pyramid.httpexceptions import HTTPNotFound
from pyramid import events
from pyramid.request import Request, reify
from pyramid.asset import resolve_asset_spec
#from purl import URL
from clld.lib.purl import URL
from clld.config import get_config

from clld.db.meta import DBSession, Base
from clld import Resource, RESOURCES
from clld.interfaces import IMenuItems, IDataTable, IIndex, IRepresentation, IMap
from clld.web.views import index_view, resource_view, robots, sitemapindex, _raise, _ping
from clld.web.subscribers import add_renderer_globals, add_localizer, init_map
from clld.web.datatables.base import DataTable
from clld.web import datatables
from clld.web.maps import Map, ParameterMap, LanguageMap


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

    def resource_url(self, obj, rsc=None, **kw):
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
        return self.route_url(route, **kw)


def menu_item(resource, ctx, req):
    """
    :return: A pair (URL, label) to create a menu item.
    """
    return req.route_url(resource), req.translate(resource.capitalize())


def ctx_factory(model, type_, req):
    """The context of a request is either a single model instance or an instance of
    DataTable incorporating all information to retrieve an appropriately filtered list
    of model instances.
    """
    if type_ == 'index':
        datatable = req.registry.getUtility(IDataTable, name=req.matched_route.name)
        return datatable(req, model)

    try:
        return model.get(req.matchdict['id'])
    except NoResultFound:
        raise HTTPNotFound()


def register_cls(interface, config, route, cls):
    config.registry.registerUtility(cls, provided=interface, name=route)


def register_app(config, pkg=None):
    """This hook can be used by apps to have some conventional locations for resources
    within the package be exploited automatically to update the registry.
    """
    if pkg is None:
        config.add_translation_dirs('clld:locale')
        config.add_route('home', '/')
        menuitems = OrderedDict(home=partial(menu_item, 'home'))
        config.registry.registerUtility(menuitems, IMenuItems)
        return

    if not hasattr(pkg, '__file__'):
        pkg = __import__(pkg)
    name = pkg.__name__
    pkg_dir = path(pkg.__file__).dirname().abspath()

    if pkg_dir.joinpath('locale').exists():
        config.add_translation_dirs('%s:locale' % name)
        config.add_translation_dirs('clld:locale')

    if pkg_dir.joinpath('appconf.ini').exists():
        cfg = get_config(pkg_dir.joinpath('appconf.ini'))
        if 'mako.directories_list' in cfg:
            cfg['mako.directories'] = cfg['mako.directories_list']
        config.add_settings(cfg)

    config.add_static_view('static', '%s:static' % name, cache_max_age=3600)
    config.add_route('home', '/')
    if pkg_dir.joinpath('views.py').exists() or pkg_dir.joinpath('views').exists():
        config.scan('%s.views' % name)

    menuitems = OrderedDict(home=partial(menu_item, 'home'))
    for plural in config.registry.settings.get(
        'clld.menuitems_list',
        ['contributions', 'parameters', 'languages', 'contributors']
    ):
        menuitems[plural] = partial(menu_item, plural)
    config.registry.registerUtility(menuitems, IMenuItems)


def includeme(config):
    config.set_request_factory(ClldRequest)

    # initialize the db connection
    engine = engine_from_config(config.registry.settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config.add_settings({'pyramid.default_locale_name': 'en'})

    # event subscribers:
    config.add_subscriber(add_localizer, events.NewRequest)
    config.add_subscriber(add_renderer_globals, events.BeforeRender)
    config.add_subscriber(init_map, events.ContextFound)

    config.add_static_view(name='clld-static', path='clld:web/static')

    #
    # make it easy to register custom functionality
    #
    config.add_directive('register_datatable', partial(register_cls, IDataTable))
    config.add_directive('register_map', partial(register_cls, IMap))

    def register_resource(config, name, model, interface):
        RESOURCES.append(Resource(name, model, interface))
        config.add_route_and_view(
            name,
            '/%s/{id:[^/\.]+}' % name,
            resource_view,
            factory=partial(ctx_factory, model, 'rsc'))

    config.add_directive('register_resource', register_resource)

    def register_adapter(config, cls, from_, to_=None, name=None):
        to_ = to_ or list(implementedBy(cls))[0]
        name = name or cls.mimetype
        config.registry.registerAdapter(cls, (from_,), to_, name=name)

    config.add_directive('register_adapter', register_adapter)

    def add_route_and_view(config, route_name, route_pattern, view, **kw):
        route_kw = {}
        factory = kw.pop('factory', None)
        if factory:
            route_kw['factory'] = factory
        config.add_route(route_name, route_pattern, **route_kw)
        config.add_view(view, route_name=route_name, **kw)

        config.add_route(route_name + '_alt', route_pattern + '.{ext}', **route_kw)
        config.add_view(view, route_name=route_name + '_alt', **kw)

    config.add_directive('add_route_and_view', add_route_and_view)

    config.add_directive('register_app', register_app)

    #
    # routes and views
    #
    # add some maintenance hatches
    config.add_route_and_view('_raise', '/_raise', _raise)
    config.add_route_and_view('_ping', '/_ping', _ping, renderer='json')

    config.add_route_and_view('robots', '/robots.txt', robots)
    config.add_route_and_view('sitemapindex', '/sitemap.xml', sitemapindex, renderer='sitemapindex.mako')

    for rsc in RESOURCES:
        name, model = rsc.name, rsc.model
        plural = name + 's'
        factory = partial(ctx_factory, model, 'index')

        config.add_route_and_view(plural, '/%s' % plural, index_view, factory=factory)
        for route_name in [plural, '%s_alt' % plural]:
            config.register_datatable(
                route_name, getattr(datatables, plural.capitalize(), DataTable))

        kw = dict(factory=partial(ctx_factory, model, 'rsc'))

        config.add_route_and_view(name, '/%s/{id:[^/\.]+}' % name, resource_view, **kw)

    # maps
    config.register_map('languages', Map)
    config.register_map('language', LanguageMap)
    config.register_map('parameter', ParameterMap)

    config.include('clld.web.adapters')
