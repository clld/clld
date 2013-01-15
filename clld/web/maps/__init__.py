try:
    from simplejson import dumps
except ImportError:
    from json import dumps

from pyramid.response import Response


class GeoJson(object):
    extension = 'geojson'
    mimetype = 'application/geojson'
    adapts = None

    def __init__(self, obj):
        self.obj = obj

    def render_to_response(self, ctx, req):
        return Response(self.render(ctx, req), content_type='application/json')

    def featurecollection_properties(self, ctx, req):
        return {}

    def feature_iterator(self, ctx, req):
        return iter([])

    def feature_properties(self, ctx, req, feature):
        return {}

    def feature_coordinates(self, ctx, req, feature):
        """
        :return: lonlat
        """
        return [0.0, 0.0]

    def render(self, ctx, req):
        features = []

        for feature in self.feature_iterator(ctx, req):
            properties = self.feature_properties(ctx, req, feature)
            if properties:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": self.feature_coordinates(ctx, req, feature)},
                    "properties": properties,
                })
        
        return dumps({
            'type': 'FeatureCollection',
            'properties': self.featurecollection_properties(ctx, req),
            'features': features,
        })


class Map(object):
    geojson_adapter = GeoJson
    style_map = None

    def __init__(self, req, eid=None):
        self.req = req
        self.eid = eid or 'map'

    def render(self):
        """
        <div id="legend">
        ...
        </div>
        <div id="map" class=""> </div>
        <script>
            WOTW.Map.init(...)
        </script>
        """
        return ''


"""
        var lon = 5;
        var lat = 40;
        var zoom = 5;
        var map, select;

        function init(){
            map = new OpenLayers.Map('map');

            var wms = new OpenLayers.Layer.WMS(
                "OpenLayers WMS",
                "http://vmap0.tiles.osgeo.org/wms/vmap0",
                {layers: 'basic'}
            );

            var sundials = new OpenLayers.Layer.Vector("KML", {
                projection: map.displayProjection,
                strategies: [new OpenLayers.Strategy.Fixed()],
                protocol: new OpenLayers.Protocol.HTTP({
                    url: "kml/sundials.kml",
                    format: new OpenLayers.Format.KML({
                        extractStyles: true,
                        extractAttributes: true
                    })
                })
            });
            
            map.addLayers([wms, sundials]);
            
            select = new OpenLayers.Control.SelectFeature(sundials);
            
            sundials.events.on({
                "featureselected": onFeatureSelect,
                "featureunselected": onFeatureUnselect
            });

            map.addControl(select);
            map.addControl(new OpenLayers.Control.LayerSwitcher());
            select.activate();   
            map.zoomToExtent(new OpenLayers.Bounds(68.774414,11.381836,123.662109,34.628906));
        }
        function onPopupClose(evt) {
            select.unselectAll();
        }
        function onFeatureSelect(event) {
            var feature = event.feature;
            // Since KML is user-generated, do naive protection against
            // Javascript.
            var content = "<h2>"+feature.attributes.name + "</h2>" + feature.attributes.description;
            if (content.search("<script") != -1) {
                content = "Content contained Javascript! Escaped content below.<br>" + content.replace(/</g, "&lt;");
            }
            popup = new OpenLayers.Popup.FramedCloud("chicken", 
                                     feature.geometry.getBounds().getCenterLonLat(),
                                     new OpenLayers.Size(100,100),
                                     content,
                                     null, true, onPopupClose);
            feature.popup = popup;
            map.addPopup(popup);
        }
        function onFeatureUnselect(event) {
            var feature = event.feature;
            if(feature.popup) {
                map.removePopup(feature.popup);
                feature.popup.destroy();
                delete feature.popup;
            }
        }
        
        
        
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



style map and rule-based styling:

    <script type="text/javascript">
        var map;

        function init() {
            map = new OpenLayers.Map('map');
            var wms = new OpenLayers.Layer.WMS(
                "OpenLayers WMS",
                "http://vmap0.tiles.osgeo.org/wms/vmap0",
                {layers: 'basic'}
            );
            
            // Create 50 random features, and give them a "type" attribute that
            // will be used to style them by size.
            var features = new Array(50);
            for (var i=0; i<features.length; i++) {
                features[i] = new OpenLayers.Feature.Vector(
                    new OpenLayers.Geometry.Point(
                        (360 * Math.random()) - 180, (180 * Math.random()) - 90
                    ), {
                        type: 5 + parseInt(5 * Math.random())
                    }
                );
            }
            
            // Create a styleMap to style your features for two different
            // render intents.  The style for the 'default' render intent will
            // be applied when the feature is first drawn.  The style for the
            // 'select' render intent will be applied when the feature is
            // selected.
            var myStyles = new OpenLayers.StyleMap({
                "default": new OpenLayers.Style({
                    pointRadius: "${type}", // sized according to type attribute
                    fillColor: "#ffcc66",
                    strokeColor: "#ff9933",
                    strokeWidth: 2,
                    graphicZIndex: 1
                }),
                "select": new OpenLayers.Style({
                    fillColor: "#66ccff",
                    strokeColor: "#3399ff",
                    graphicZIndex: 2
                })
            });
            
            // Create a vector layer and give it your style map.
            var points = new OpenLayers.Layer.Vector("Points", {
                styleMap: myStyles,
                rendererOptions: {zIndexing: true}
            });
            points.addFeatures(features);
            map.addLayers([wms, points]);
            
            // Create a select feature control and add it to the map.
            var select = new OpenLayers.Control.SelectFeature(points, {hover: true});
            map.addControl(select);
            select.activate();
            
            map.setCenter(new OpenLayers.LonLat(0, 0), 1);
        }
    </script>
    
graphic names:
    
// user custom graphicname
OpenLayers.Renderer.symbol.lightning = [0, 0, 4, 2, 6, 0, 10, 5, 6, 3, 4, 5, 0, 0];
OpenLayers.Renderer.symbol.rectangle = [0, 0, 4, 0, 4, 10, 0, 10, 0, 0];
OpenLayers.Renderer.symbol.church = [4, 0, 6, 0, 6, 4, 10, 4, 10, 6, 6, 6, 6, 14, 4, 14, 4, 6, 0, 6, 0, 4, 4, 4, 4, 0];
var map;

function init(){
    // allow testing of specific renderers via "?renderer=Canvas", etc
    var renderer = OpenLayers.Util.getParameters(window.location.href).renderer;
    renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers;

    map = new OpenLayers.Map('map', {
        controls: []
    });
    
    // list of well-known graphic names
    var graphics = ["star", "cross", "x", "square", "triangle", "circle", "lightning", "rectangle", "church"];
    
    // Create one feature for each well known graphic.
    // Give features a type attribute with the graphic name.
    var num = graphics.length;
    var slot = map.maxExtent.getWidth() / num;
    var features = Array(num);
    for (var i = 0; i < graphics.length; ++i) {
        lon = map.maxExtent.left + (i * slot) + (slot / 2);
        features[i] = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(map.maxExtent.left + (i * slot) + (slot / 2), 0), {
            type: graphics[i]
        });
    }
    
    // Create a style map for painting the features.
    // The graphicName property of the symbolizer is evaluated using
    // the type attribute on each feature (set above).
    var styles = new OpenLayers.StyleMap({
        "default": {
            graphicName: "${type}",
            pointRadius: 10,
            strokeColor: "fuchsia",
            strokeWidth: 2,
            fillColor: "lime",
            fillOpacity: 0.6
        },
        "select": {
            pointRadius: 20,
            fillOpacity: 1,
            rotation: 45    // this is how we get a diamond from a square!, and a top-down-triangle!
        }
    });
    
    // Create a vector layer and give it your style map.
    var layer = new OpenLayers.Layer.Vector("Graphics", {
        styleMap: styles,
        isBaseLayer: true,
        renderers: renderer
    });
    layer.addFeatures(features);
    map.addLayer(layer);
    
    // Create a select feature control and add it to the map.
    var select = new OpenLayers.Control.SelectFeature(layer, {
        hover: true
    });
    map.addControl(select);
    select.activate();
    
    map.zoomToMaxExtent();
}


info window:

http://gis.stackexchange.com/questions/42401/how-can-i-add-an-infowindow-to-an-openlayers-geojson-layer
"""