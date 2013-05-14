from markupsafe import Markup
from pyramid.renderers import render

from clld.interfaces import IDataTable, IMapMarker
from clld.web.util import helpers
from clld.web.adapters import GeoJsonLanguages


class Layer(object):
    """A layer in our terminology is a FeatureCollection in geojson and a FeatureGroup
    in leaflet, i.e. a bunch of points on the map.
    """
    def __init__(self, id_, name, data, **kw):
        self.id = id_
        self.name = name
        self.data = data
        for k, v in kw.items():
            setattr(self, k, v)


class Map(object):
    """Map objects bridge the technology divide between server side python code and
    client side leaflet maps.
    """
    def __init__(self, ctx, req, eid='map'):
        self.req = req
        self.ctx = ctx
        self.eid = eid
        self._layers = None
        self.map_marker = req.registry.getUtility(IMapMarker)

    @property
    def layers(self):
        if self._layers is None:
            self._layers = list(self.get_layers())
        return self._layers

    def get_layers(self):
        route_params = {'ext': 'geojson'}
        if not IDataTable.providedBy(self.ctx):
            route_params['id'] = self.ctx.id
        route_name = self.req.matched_route.name
        if not route_name.endswith('_alt'):
            route_name += '_alt'
        yield Layer(
            getattr(self.ctx, 'id', 'id'),
            '%s' % self.ctx,
            self.req.route_url(route_name, **route_params))

    def options(self):
        return {}

    def render(self):
        return Markup(render(
            'clld:web/templates/map.mako', {'map': self}, request=self.req))


class ParameterMap(Map):
    def get_layers(self):
        if self.ctx.domain:
            for de in self.ctx.domain:
                yield Layer(
                    de.id,
                    de.name,
                    self.req.resource_url(
                        self.ctx, ext='geojson', _query=dict(domainelement=str(de.id))
                    ),
                    marker=helpers.map_marker_img(self.req, de, marker=self.map_marker))
        else:
            yield Layer(
                self.ctx.id, self.ctx.name, self.req.resource_url(self.ctx, ext='geojson'))

    def options(self):
        return {'info_query': {'parameter': self.ctx.pk}, 'hash': True}


class _GeoJson(GeoJsonLanguages):
    def feature_iterator(self, ctx, req):
        return [ctx]


class LanguageMap(Map):
    def get_layers(self):
        geojson = _GeoJson(self.ctx)
        yield Layer(
            self.ctx.id, self.ctx.name, geojson.render(self.ctx, self.req, dump=False))

    def options(self):
        return {
            'center': [self.ctx.latitude, self.ctx.longitude],
            'zoom': 3,
            'no_popup': True,
            'sidebar': True}
