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


    var selectedFeature;
    var selectCtrl;


    function onFeatureSelectCallback(data) {
        popup = new OpenLayers.Popup.FramedCloud("chicken",
                selectedFeature.geometry.getBounds().getCenterLonLat(),
                null,
                data,
                null, false, null);
        selectedFeature.popup = popup;
        CLLD.Map.map.addPopup(popup);
    }

    function onFeatureSelect(feature) {
        var route = CLLD.Map.options.info_route == undefined ? 'language_alt' : CLLD.Map.options.info_route;

        selectedFeature = feature;
        $.get(
            CLLD.route_url(route, {'id': feature.data.id, 'ext': 'snippet.html'}, CLLD.Map.options.info_query),
            CLLD.Map.options.info_query == undefined ? {} : CLLD.Map.options.info_query,
            function(data, textStatus, jqXHR) {
                onFeatureSelectCallback(data);
            },
            'html'
        );
    }

    function onFeatureUnselect(feature) {
        CLLD.Map.map.removePopup(feature.popup);
        feature.popup.destroy();
        feature.popup = null;
    }


    var _init = function (data_layers, options) {  // TODO: per-layer options! in particular style map
        var i, layer, spec, styles = CLLD.Map.style_maps['default'];

        CLLD.Map.options = options == undefined ? {} : options;

        if (CLLD.Map.options.style_map) {
            styles = CLLD.Map.style_maps[CLLD.Map.options.style_map];
        }

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
            zoom: 1
        });
        CLLD.Map.map.addControl(new OpenLayers.Control.LayerSwitcher());

        // more info: http://docs.openlayers.org/library/feature_styling.html
        // or use pie charts from google via externalGraphic!

        for (i=0; i<data_layers.length; i++) {
            spec = data_layers[i];
            layer = new OpenLayers.Layer.Vector(spec.name, {
                styleMap: spec.style_map === undefined ? styles : spec.style_map,
                displayInLayerSwitcher: false,
                rendererOptions: {zIndexing: true},
                projection: new OpenLayers.Projection('EPSG:4326'),
                strategies: [new OpenLayers.Strategy.Fixed()],
                protocol: new OpenLayers.Protocol.HTTP({
                    url: spec.url,
                    format: new OpenLayers.Format.GeoJSON()
                })
            });
            CLLD.Map.layers.push(layer);
            CLLD.Map.map.addLayer(layer);
        }

        var highlightCtrl = new OpenLayers.Control.SelectFeature(
            CLLD.Map.layers,
            {
                hover: true,
                highlightOnly: true,
                renderIntent: "temporary"
            }
        );

        selectCtrl = new OpenLayers.Control.SelectFeature(
            CLLD.Map.layers,
            {
                onUnselect: onFeatureUnselect,
                onSelect: onFeatureSelect,
            }
        );

        CLLD.Map.map.addControl(highlightCtrl);
        CLLD.Map.map.addControl(selectCtrl);

        highlightCtrl.activate();
        selectCtrl.activate();

        //CLLD.Map.map.zoomToMaxExtent();
    };

    return {
        map: undefined,
        layers: [],
        init: _init,
        url: function() {
        },
        getLayer: function(spec) {
            var i, layer;
            spec = spec === undefined ? 0 : spec;

            if (typeof spec == 'string') {
                for (i=0; i<CLLD.Map.layers.length; i++) {
                    if (CLLD.Map.layers[i].name == spec) {
                        return CLLD.Map.layers[i];
                    }
                }
            } else {
                return CLLD.Map.layers[spec];
            }
            return undefined;
        },
        showInfoWindow: function(property, value, layer) {
            if (selectedFeature) {
                selectCtrl.unselect(selectedFeature);
            }
            var features;
            layer = CLLD.Map.getLayer(layer);
            features = layer.getFeaturesByAttribute(property, value)
            if (features) {
                selectCtrl.select(features[0]);
            }
        },
        toggleLayer: function(layer, ctrl) {
            layer = CLLD.Map.getLayer(layer);
            layer.display(!$(ctrl).prop('checked'));
            $(ctrl).prop('checked', !$(ctrl).prop('checked'));
        },
        style_maps: {'default': styles}
    }
})();
