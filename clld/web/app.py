from functools import partial
from collections import OrderedDict

from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from pyramid.httpexceptions import HTTPNotFound
from pyramid import events

from clld.db.meta import (
    DBSession,
    Base,
)
from clld.db.models import MODELS
from clld.interfaces import IMenuItems, IDataTable, IIndex, IRepresentation, IMap
from clld.web.views import index_view, resource_view, robots, sitemapindex
from clld.web.subscribers import add_renderer_globals, add_localizer, init_map
from clld.web.datatables.base import DataTable
from clld.web import datatables
from clld.web.maps import Map


def menu_item(resource, ctx, req):
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
        return DBSession.query(model).filter(model.id==req.matchdict['id']).one()
    except NoResultFound:
        raise HTTPNotFound()


def register_cls(interface, config, route, cls):
    config.registry.registerUtility(cls, provided=interface, name=route)


def includeme(config):
    engine = engine_from_config(config.registry.settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config.add_settings({'pyramid.default_locale_name':'en'})
    config.add_subscriber(add_renderer_globals, events.BeforeRender)
    config.add_subscriber(add_localizer, events.NewRequest)
    config.add_subscriber(init_map, events.ContextFound)
    config.add_translation_dirs('clld:locale')

    config.add_static_view(name='clld-static', path='clld:web/static')

    config.add_directive('register_datatable', partial(register_cls, IDataTable))
    config.add_directive('register_map', partial(register_cls, IMap))

    def add_route_and_view(config, route_name, route_pattern, view, **kw):
        route_kw = {}
        factory = kw.pop('factory', None)
        if factory:
            route_kw['factory'] = factory
        config.add_route(route_name, route_pattern, **route_kw)
        config.add_view(view, route_name=route_name, **kw)

    config.add_directive('add_route_and_view', add_route_and_view)

    config.add_route('home', '/')
    menuitems = OrderedDict(home=partial(menu_item, 'home'))

    config.add_route_and_view('robots', '/robots.txt', robots)
    config.add_route_and_view('sitemapindex', '/sitemap.xml', sitemapindex, renderer='sitemapindex.mako')

    for name, model in MODELS.items():
        plural = name + 's'
        factory = partial(ctx_factory, model, 'index')

        for route_name, pattern in [
            (plural, '/%s' % plural), ('%s_alt' % plural, '/%s.{ext}' % plural),
        ]:
            config.add_route_and_view(route_name, pattern, index_view, factory=factory)
            config.register_datatable(
                route_name, getattr(datatables, plural.capitalize(), DataTable))

        kw = dict(factory=partial(ctx_factory, model, 'rsc'))
        config.add_route_and_view(name, '/%s/{id:[^/\.]+}' % name, resource_view, **kw)
        config.add_route_and_view('%s_alt' % name, '/%s/{id:[^/\.]+}.{ext}' % name, resource_view, **kw)

        if plural in config.registry.settings.get(
            'clld.menuitems', 'contributions parameters languages').split():
            menuitems[plural] = partial(menu_item, plural)

    #
    # TODO: register maps!
    #
    config.register_map('languages', Map)

    config.registry.registerUtility(menuitems, IMenuItems)
    config.include('clld.web.adapters')
