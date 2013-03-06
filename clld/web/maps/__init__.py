try:
    from simplejson import dumps
except ImportError:
    from json import dumps

from markupsafe import Markup
from pyramid.response import Response
from pyramid.renderers import render

from clld.interfaces import IDataTable, IMapMarker
from clld.web.util import htmllib
from clld.web.util import helpers
from clld.web.adapters import GeoJsonLanguages


class Map(object):
    style_map = None

    def __init__(self, ctx, req, eid=None):
        self.req = req
        self.ctx = ctx
        self.eid = eid or 'map'
        self._layers = None
        self.map_marker = req.registry.queryUtility(IMapMarker)

    @property
    def layers(self):
        if self._layers is None:
            self._layers = self.get_layers()
        return self._layers

    def get_layers(self):
        route_params = {'ext': 'geojson'}
        if not IDataTable.providedBy(self.ctx):
            route_params['id'] = self.ctx.id
        route_name = self.req.matched_route.name
        if not route_name.endswith('_alt'):
            route_name += '_alt'
        return [{
            'name': getattr(self.ctx, 'name', 'GeoJSON layer'),
            'url': self.req.route_url(route_name, **route_params)}]

    def options(self):
        return {}

    def render(self):
        return Markup(render(
            'clld:web/templates/map.mako', {'map': self}, request=self.req))


class ParameterMap(Map):
    def get_layers(self):
        if self.ctx.domain:
            return [{
                'name': de.name,
                'marker': helpers.map_marker_img(self.req, de, marker=self.map_marker),
                'url': self.req.resource_url(
                    self.ctx, ext='geojson', _query=dict(domainelement=str(de.id))),
            } for de in self.ctx.domain]
        return [{
            'name': self.ctx.name, 'url': self.req.resource_url(self.ctx, ext='geojson')}]

    def options(self):
        return {'info_query': {'parameter': self.ctx.pk}}


class _GeoJson(GeoJsonLanguages):
    def feature_iterator(self, ctx, req):
        return [ctx]


class LanguageMap(Map):
    def get_layers(self):
        geojson = _GeoJson(self.ctx)
        return [{
            'name': self.ctx.name,
            'data': geojson.render(self.ctx, self.req, dump=False),
        }]

    def options(self):
        return {'center': [self.ctx.longitude, self.ctx.latitude], 'zoom': 3, 'no_popup': True, 'sidebar': True}


"""
resize marker:

    <script type="text/javascript">
        var map, layer;
        var size, icon;

        function init(){
            map = new OpenLayers.Map('map');
            layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                "http://vmap0.tiles.osgeo.org/wms/vmap0", {layers: 'basic'} );

            map.addLayer(layer);
            var markers = new OpenLayers.Layer.Markers( "Markers" );
            map.addLayer(markers);

            size = new OpenLayers.Size(21, 25);
            calculateOffset = function(size) {
                        return new OpenLayers.Pixel(-(size.w/2), -size.h); };
            icon = new OpenLayers.Icon(
                'http://www.openlayers.org/dev/img/marker.png',
                size, null, calculateOffset);
            markers.addMarker(
                new OpenLayers.Marker(new OpenLayers.LonLat(-71,40), icon));

            map.addControl(new OpenLayers.Control.LayerSwitcher());
            map.zoomToMaxExtent();
        }

        function resize() {

            size = new OpenLayers.Size(size.w + 10, size.h + 10);
            icon.setSize(size);

        }
    </script>

nav toolbar:

            var panel = new OpenLayers.Control.NavToolbar();
            map.addControl(panel);

info window:

http://gis.stackexchange.com/questions/42401/how-can-i-add-an-infowindow-to-an-openlayers-geojson-layer
"""
