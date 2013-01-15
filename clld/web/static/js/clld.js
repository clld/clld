CLLD = {
    'routes': {
        'language': '/language/{id}',
        'language_alt': '/language/{id}.{ext}'
    },
};

CLLD.test = function(x){return x};

CLLD.route_url = function(route, data, query) {
    var key, url = CLLD.routes[route], sep = '?';

    for (key in data) {
        if (data.hasOwnProperty(key)) {
            url = url.replace('{'+key+'}', data[key]);
        }
    }

    if (/\?/.test(url)) {
        sep = '&';
    }

    if (query) {
        url += sep + $.param(query);
    }

    return url;
}


CLLD.Map = (function(){
    var styles = new OpenLayers.StyleMap({
        "default": {
            pointRadius: 8,
            strokeColor: "black",
            strokeWidth: 1,
            fillColor: "#f89117",
            fillOpacity: 0.8//,
            //graphicXOffset: 50,
            //graphicYOffset: 50,
            //graphicZIndex: 20
        },
        "temporary": {
            pointRadius: 12,
            fillOpacity: 1,
            label : "${name}",
            fontColor: "black",
            fontSize: "12px",
            fontFamily: "Courier New, monospace",
            fontWeight: "bold",
            labelAlign: "cm",
            labelOutlineColor: "white",
            labelOutlineWidth: 3
        },
        "select": {
            externalGraphic: "http://chart.googleapis.com/chart?cht=p&chs=38x38&chd=t:60,40&chco=FF0000|00FF00&chf=bg,s,FFFFFF00",
            label: "",
            //pointRadius: 25,
            graphicWidth: 38,
            graphicHeight: 38
        }
    });

    var _init = function (data_layers, options) {
        var i, route, layer, layers = [], styles = CLLD.Map.style_maps['default'];

        options = options == undefined ? {} : options;

        if (options.style_map) {
            styles = CLLD.Map.style_maps[options.style_map];
        }

        route = options.info_route == undefined ? 'language_alt' : options.info_route;

        CLLD.Map.map = new OpenLayers.Map('map', {
            projection: 'EPSG:3857',
            layers: [
                new OpenLayers.Layer.Google(
                    "Google Physical",
                    {type: google.maps.MapTypeId.TERRAIN}
                ),
                new OpenLayers.Layer.Google(
                    "Google Streets", // the default
                    {numZoomLevels: 20}
                ),
                new OpenLayers.Layer.Google(
                    "Google Hybrid",
                    {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}
                ),
                new OpenLayers.Layer.Google(
                    "Google Satellite",
                    {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}
                )
            ],
            center: new OpenLayers.LonLat(10.2, 48.9)
                // Google.v3 uses web mercator as projection, so we have to
                // transform our coordinates
                .transform('EPSG:4326', 'EPSG:3857'),
            zoom: 3
        });
        CLLD.Map.map.addControl(new OpenLayers.Control.LayerSwitcher());

        // more info: http://docs.openlayers.org/library/feature_styling.html
        // or use pie charts from google via externalGraphic!

        for (i=0; i<data_layers.length; i++) {
            layer = new OpenLayers.Layer.Vector(data_layers[i][0], {
                styleMap: styles,
                displayInLayerSwitcher: false,
                rendererOptions: {zIndexing: true},
                projection: new OpenLayers.Projection('EPSG:4326'),
                strategies: [new OpenLayers.Strategy.Fixed()],
                protocol: new OpenLayers.Protocol.HTTP({
                    url: data_layers[i][1],
                    format: new OpenLayers.Format.GeoJSON()
                })
            });
            layers.push(layer);
            CLLD.Map.layers[data_layers[i][0]] = layer;
            CLLD.Map.map.addLayer(layer);
        }

        var highlightCtrl = new OpenLayers.Control.SelectFeature(
            layers,
            {
                hover: true,
                highlightOnly: true,
                renderIntent: "temporary"
            }
        );

        var selectedFeature;

        function onFeatureSelect(data) {
            popup = new OpenLayers.Popup.FramedCloud("chicken",
                    selectedFeature.geometry.getBounds().getCenterLonLat(),
                    null,
                    data,
                    null, false, null);
            selectedFeature.popup = popup;
            CLLD.Map.map.addPopup(popup);
        }

        function onFeatureUnselect(feature) {
            CLLD.Map.map.removePopup(feature.popup);
            feature.popup.destroy();
            feature.popup = null;
        }

        var selectCtrl = new OpenLayers.Control.SelectFeature(
            layers,
            {
                onUnselect: onFeatureUnselect,
                onSelect: function(feature){
                    selectedFeature = feature;
                    $.get(
                        CLLD.route_url(route, {'id': feature.data.id, 'ext': 'snippet.html'}, options.info_query),
                        options.info_query == undefined ? {} : options.info_query,
                        function(data, textStatus, jqXHR) {
                            onFeatureSelect(data);
                        },
                        'html'
                    );
                }
            }
        );

        CLLD.Map.map.addControl(highlightCtrl);
        CLLD.Map.map.addControl(selectCtrl);

        highlightCtrl.activate();
        selectCtrl.activate();

        CLLD.Map.map.zoomToMaxExtent();
    };

    return {
        map: undefined,
        layers: {},
        init: _init,
        url: function() {},
        style_maps: {'default': styles}
    }
})();
