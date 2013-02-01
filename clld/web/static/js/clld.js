CLLD = {
    'routes': {
        'language': '/language/{id}',
        'language_alt': '/language/{id}.{ext}'
    }
};

CLLD.route_url = function(route, data, query) {
    var key,
        url = CLLD.routes[route],
        sep = '?';

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


CLLD.Feed = (function(){
    var _init = function(spec) {
        var feed = new google.feeds.Feed(spec.url);

        feed.setNumEntries(spec.numEntries == undefined ? 4 : spec.numEntries);
        feed.load(function(result) {
            if (!result.error) {
                var title = spec.title == undefined ? result.feed.title : spec.title
                var content = '<h3><a href="'+result.feed.link+'">'+title+'</a></h3>';
                for (var j = 0; j < result.feed.entries.length; j++) {
                    var entry = result.feed.entries[j];
                    content += '<h4><a href="'+entry.link+'">'+entry.title+'</a></h4>';
                    content += '<p class="muted"><small>'+entry.publishedDate+'</small></p>';
                    content += '<p>'+entry.contentSnippet+'</p>';
                }
                $('#'+spec.eid).html(content);
            }
        });
    }

    return {
        init: _init
    }
})();


CLLD.Modal = (function(){
    var _show = function(title, url) {
        $('#ModalLabel').html(title);
        $('#ModalBody').load(url);
        $('#Modal').modal('show');
    }

    return {
        show: _show
    }
})();


CLLD.DataTable = (function(){

    var _init = function(eid, toolbar, options) {
        var col;

        options = options === undefined ? {} : options;

        $.extend($.fn.dataTable.defaults, {
            "fnServerParams": function (aoData) {
		aoData.push({"name": "__eid__", "value": "${datatable.eid}"});
            },
            "fnInitComplete": function(oSettings) {
                var i, ctrl;
                for (i=0 ; i<oSettings.aoPreSearchCols.length ; i++) {
                    if(oSettings.aoPreSearchCols[i].sSearch.length > 0) {
			ctrl = $("tfoot .control")[i];
			ctrl = $(ctrl);
			if (ctrl.length) {
			    ctrl.val(oSettings.aoPreSearchCols[i].sSearch);
			}
                    }
                }
            }
        });

        $.extend($.fn.dataTableExt.oStdClasses, {
            "sWrapper": "dataTables_wrapper form-inline"
        } );

        /* API method to get paging information */
        $.fn.dataTableExt.oApi.fnPagingInfo = function (oSettings) {
            return {
		"iStart":         oSettings._iDisplayStart,
		"iEnd":           oSettings.fnDisplayEnd(),
		"iLength":        oSettings._iDisplayLength,
		"iTotal":         oSettings.fnRecordsTotal(),
		"iFilteredTotal": oSettings.fnRecordsDisplay(),
		"iPage":          Math.ceil( oSettings._iDisplayStart / oSettings._iDisplayLength ),
		"iTotalPages":    Math.ceil( oSettings.fnRecordsDisplay() / oSettings._iDisplayLength )
            };
        };

        /* Bootstrap style pagination control */
        $.extend($.fn.dataTableExt.oPagination, {
            "bootstrap": {
		"fnInit": function(oSettings, nPaging, fnDraw) {
		    var oLang = oSettings.oLanguage.oPaginate;
                    var fnClickHandler = function ( e ) {
			e.preventDefault();
			if ( oSettings.oApi._fnPageChange(oSettings, e.data.action) ) {
			    fnDraw( oSettings );
			}
		    };

		    $(nPaging).addClass('pagination').append(
			'<ul>'+
			    '<li class="prev disabled"><a href="#">&larr; '+oLang.sPrevious+'</a></li>'+
			    '<li class="next disabled"><a href="#">'+oLang.sNext+' &rarr; </a></li>'+
			'</ul>'
		    );
		    var els = $('a', nPaging);
		    $(els[0]).bind( 'click.DT', { action: "previous" }, fnClickHandler );
		    $(els[1]).bind( 'click.DT', { action: "next" }, fnClickHandler );
		},
		"fnUpdate": function ( oSettings, fnDraw ) {
		    var iListLength = 5;
		    var oPaging = oSettings.oInstance.fnPagingInfo();
		    var an = oSettings.aanFeatures.p;
		    var i, j, sClass, iStart, iEnd, iHalf=Math.floor(iListLength/2);

		    if ( oPaging.iTotalPages < iListLength) {
			iStart = 1;
			iEnd = oPaging.iTotalPages;
		    } else if ( oPaging.iPage <= iHalf ) {
			iStart = 1;
			iEnd = iListLength;
		    } else if ( oPaging.iPage >= (oPaging.iTotalPages-iHalf) ) {
			iStart = oPaging.iTotalPages - iListLength + 1;
                        iEnd = oPaging.iTotalPages;
		    } else {
			iStart = oPaging.iPage - iHalf + 1;
			iEnd = iStart + iListLength - 1;
		    }

		    for ( i=0, iLen=an.length ; i<iLen ; i++ ) {
			// Remove the middle elements
			$('li:gt(0)', an[i]).filter(':not(:last)').remove();

			// Add the new list items and their event handlers
			for ( j=iStart ; j<=iEnd ; j++ ) {
			    sClass = (j==oPaging.iPage+1) ? 'class="active"' : '';
			    $('<li '+sClass+'><a href="#">'+j+'</a></li>')
			    .insertBefore( $('li:last', an[i])[0] )
			    .bind('click', function (e) {
				e.preventDefault();
				oSettings._iDisplayStart = (parseInt($('a', this).text(),10)-1) * oPaging.iLength;
				fnDraw( oSettings );
			    } );
			}

			// Add / remove disabled classes from the static elements
			if ( oPaging.iPage === 0 ) {
			    $('li:first', an[i]).addClass('disabled');
			} else {
			    $('li:first', an[i]).removeClass('disabled');
		    	}

			if ( oPaging.iPage === oPaging.iTotalPages-1 || oPaging.iTotalPages === 0 ) {
			    $('li:last', an[i]).addClass('disabled');
			} else {
			    $('li:last', an[i]).removeClass('disabled');
			}
		    }
		}
            }
        } );

        CLLD.DataTable.dt = $('#'+eid).dataTable(options);
        $('.dataTables_filter').hide();
        if (toolbar) {
            $("div.dt-toolbar").html(toolbar);
        }
        $('#searchCol').change(function(){CLLD.DataTable.dt.fnFilter($('.dataTables_filter input').val())});
        $('#'+eid+' tbody td button.details').live('click', function () {
            var nTr = $(this).parents('tr')[0];
            if (CLLD.DataTable.dt.fnIsOpen(nTr)) {
                CLLD.DataTable.dt.fnClose( nTr );
            } else {
                $.get($(this).attr('href'), {}, function(data, textStatus, jqXHR) {
                    CLLD.DataTable.dt.fnOpen( nTr, data, 'details' );
                }, 'html');
            }
        });

        $("tfoot input").keyup( function () {
            /* Filter on the column (the index) of this element */
            CLLD.DataTable.dt.fnFilter(this.value, $("tfoot .control").index(this));
        });

	$("tfoot select").change( function () {
            /* Filter on the column (the index) of this element */
            CLLD.DataTable.dt.fnFilter($(this).val(), $("tfoot .control").index(this));
        });

        var dl = '';
        for (i=0; i < options.aoColumns.length; i++) {
            col = options.aoColumns[i];
            if (col.sDescription) {
                dl += '<dt>'+col.sTitle+'</dt><dd>'+col.sDescription+'</dd>';
            }
        }

        if (dl) {
        	$('#cdOpener').popover({html: true, content: '<dl>'+dl+'</dl>', title: 'Column Descriptions', trigger: 'click', placement: 'left'});
        } else {
            $('#cdOpener').hide();
        }
    };

    return {
        dt: undefined,
        init: _init
    }
})();


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
        var i, layer, layer_options, spec, center, zoom,
            styles = CLLD.Map.style_maps['default'];

        // World Geodetic System 1984 projection (lon/lat)
        var WGS84 = new OpenLayers.Projection("EPSG:4326");

        // WGS84 Google Mercator projection (meters)
        //var WGS84_google_mercator = new OpenLayers.Projection("EPSG:900913");
        var WGS84_google_mercator = new OpenLayers.Projection("EPSG:3857");

        CLLD.Map.options = options == undefined ? {} : options;

        center = CLLD.Map.options.center == undefined ? (0, 0) : CLLD.Map.options.center;
        zoom = CLLD.Map.options.zoom == undefined ? 2 : CLLD.Map.options.zoom;

        if (CLLD.Map.options.style_map) {
            styles = CLLD.Map.style_maps[CLLD.Map.options.style_map];
        }

        CLLD.Map.map = new OpenLayers.Map('map', {
            projection: WGS84_google_mercator,
            layers: [
                new OpenLayers.Layer.Google(
                    "Google Physical",
                    {type: google.maps.MapTypeId.TERRAIN, minZoomLevel: 1}
                )/*,
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
                )*/
            ],
            maxExtent: new OpenLayers.Bounds(-180, -85.0511, 180, 85.0511).transform(WGS84, WGS84_google_mercator)
        });

        CLLD.Map.map.setCenter(new OpenLayers.LonLat(center[0], center[1])
                               .transform(WGS84, WGS84_google_mercator), zoom);

        CLLD.Map.map.addControl(new OpenLayers.Control.LayerSwitcher());

        // more info: http://docs.openlayers.org/library/feature_styling.html
        // or use pie charts from google via externalGraphic!

        var geojsonParser = new OpenLayers.Format.GeoJSON({
                'internalProjection': WGS84_google_mercator,
                'externalProjection': WGS84
            });

        for (i=0; i<data_layers.length; i++) {
            spec = data_layers[i];

            layer_options = {
                styleMap: spec.style_map === undefined ? styles : spec.style_map,
                displayInLayerSwitcher: false,
                rendererOptions: {zIndexing: true},
                projection: WGS84
            }

            if (spec.url && !spec.data) {
                layer_options.strategies = [new OpenLayers.Strategy.Fixed()];
                layer_options.protocol = new OpenLayers.Protocol.HTTP({
                    url: spec.url,
                    format: new OpenLayers.Format.GeoJSON()
                });
            }

            layer = new OpenLayers.Layer.Vector(spec.name, layer_options);

            if (spec.data) {
                layer.addFeatures(geojsonParser.read(spec.data));
            }

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
                onSelect: onFeatureSelect
            }
        );

        CLLD.Map.map.addControl(highlightCtrl);
        CLLD.Map.map.addControl(selectCtrl);

        highlightCtrl.activate();
        selectCtrl.activate();

        CLLD.Map.map.zoomToMaxExtent();
        //var mapextent = new OpenLayers.Bounds(-179, -80, 179, 80)
        //    .transform(WGS84, map.getProjectionObject());
        //CLLD.Map.map.zoomToExtent(mapextent);
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
