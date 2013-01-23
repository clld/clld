try:
    from simplejson import dumps
except ImportError:
    from json import dumps

from markupsafe import Markup
from pyramid.response import Response
from pyramid.renderers import render

from clld.interfaces import IDataTable
from clld.web.util import htmllib


class Map(object):
    style_map = None

    def __init__(self, ctx, req, eid=None):
        self.req = req
        self.ctx = ctx
        self.eid = eid or 'map'

    def layers(self):
        route_params = {'ext': 'geojson'}
        if not IDataTable.providedBy(self.ctx):
            route_params['id'] = self.ctx.id
        route_name = self.req.matched_route.name
        if not route_name.endswith('_alt'):
            route_name += '_alt'
        return [[getattr(self.ctx, 'name', 'GeoJSON layer'), self.req.route_url(route_name, **route_params)]]

    def render(self):
        return Markup(render(
            'clld:web/templates/map.mako',
            {'map': self,
             #'options': Markup(dumps(self.options))
             },
            request=self.req))


class ParameterMap(Map):
    def layers(self):
        if self.ctx.domain:
            return [[de.name, self.req.route_url('parameter_alt', id=self.ctx.id, ext='geojson', _query=dict(domainelement=str(de.id)))] for de in self.ctx.domain]
        return [[self.ctx.name, self.req.route_url('parameter_alt', id=self.ctx.id, ext='geojson')]]



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
