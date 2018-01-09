# coding: utf8
from __future__ import unicode_literals, print_function, division
from xml.etree.ElementTree import fromstring

from pyramid.config import Configurator
from mock import Mock


def main(global_config, **settings):
    """called when bootstrapping a pyramid app using clld/tests/test.ini."""
    from clld import interfaces
    from clld.web.app import MapMarker
    from clld.web.adapters.base import Representation

    settings['mako.directories'] = ['clld:web/templates']
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.registry.registerUtility(MapMarker(), interfaces.IMapMarker)
    config.register_staticresource('css', 'clld:web/static/notexisting.css')
    config.register_staticresource('js', 'clld:web/static/notexisting.js')
    config.register_adapter(Representation, Mock, name='test')
    config.register_menu(('home', lambda ctx, req: (req.resource_url(req.dataset), 'tt')))
    return config.make_wsgi_app()


def handle_dt(req, dt_cls, model, **kw):
    dt = dt_cls(req, model, **kw)
    dt.render()
    for item in dt.get_query():
        for col in dt.cols:
            col.format(item)
    assert isinstance(dt.options, dict)
    return dt


class XmlResponse(object):

    """Wrapper for XML responses."""

    ns = None

    def __init__(self, response):
        self.raw = response.body
        self.root = fromstring(response.body)

    def findall(self, name):
        if not name.startswith('{') and self.ns:
            name = '{%s}%s' % (self.ns, name)
        return self.root.findall('.//%s' % name)

    def findone(self, name):
        _all = self.findall(name)
        if _all:
            return _all[0]
