CLLD = {
    'routes': {},
    'base_url': ''
};


CLLD.route_url = function(route, data, query) {
    var key,
        url = CLLD.base_url + CLLD.routes[route],
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


CLLD.TreeView = (function(){
    return {
        init: function() {
            $('input.treeview').change(function () {
                var icon = $('label[for="'+this.getAttribute('id')+'"]').children('i');
                if ($(this).prop('checked')) {
                    icon.addClass('icon-chevron-down');
                    icon.removeClass('icon-chevron-right');
                } else {
                    icon.addClass('icon-chevron-right');
                    icon.removeClass('icon-chevron-down');
                }
            });
        },
        show: function(level) {
            $('input.level'+level+':not(:checked)').trigger('click');
        },
        hide: function(level) {
            $('input.level'+level+':checked').trigger('click');
        }
    }
})();


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
                aoData.push({"name": "__eid__", "value": eid});
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
            $('#cdOpener').clickover({
                html: true,
                content: '<dl>'+dl+'</dl>',
                title: 'Column Descriptions',
                placement: 'left',/*function (context, source) {
                    var position = $(source).position();
                    if (position.top < 80){
                        return "bottom";
                    }
                    return "left";
                },*/
                trigger: "click"
            });
        } else {
            $('#cdOpener').hide();
        }

        for (i=0; i < options.aoColumns.length; i++) {
            col = options.aoColumns[i];
            if (col.sFilter) {
                CLLD.DataTable.dt.fnFilter(col.sFilter, i);
            }
        }

    };

    return {
        dt: undefined,
        init: _init,
        current_url: function(fmt) {
            var url, parts,
                query = {'sEcho': 1},
                oSettings = CLLD.DataTable.dt.fnSettings();
            query.iSortingCols = oSettings.aaSorting.length;
            for (i=0; i < oSettings.aaSorting.length; i++) {
                query['iSortCol_' + i] = oSettings.aaSorting[i][0];
                query['sSortDir_' + i] = oSettings.aaSorting[i][1];
            }
            for (i=0; i < oSettings.aoPreSearchCols.length; i++) {
                if (oSettings.aoPreSearchCols[i].sSearch) {
                    query['sSearch_' + i] = oSettings.aoPreSearchCols[i].sSearch;
                }
            }
            parts = oSettings.sAjaxSource.split('?', 2);
            if (parts.length == 1) {
                url = oSettings.sAjaxSource + '.' + fmt + '?'
            } else {
                url = parts[0] + '.' + fmt + '?' + parts[1] + '&'
            }
            return url + $.param(query);
        }
    }
})();


/*
 * Manager for a leaflet map
 */
CLLD.Map = (function(){
    function _openPopup(layer, html) {
        if (!CLLD.Map.popup) {
            CLLD.Map.popup = L.popup();
        }
        CLLD.Map.popup.setLatLng(layer.getLatLng());
        CLLD.Map.popup.setContent(html);
        CLLD.Map.map.openPopup(CLLD.Map.popup);
    }

    function _showInfoWindow(layer) {
        var route = CLLD.Map.options.info_route == undefined ? 'language_alt' : CLLD.Map.options.info_route;

        if (CLLD.Map.marker_map.hasOwnProperty(layer)) {
            // allow opening the info window by language id
            layer = CLLD.Map.marker_map[layer];
        }
        $.get(
            CLLD.route_url(
                route,
                {'id': layer.feature.properties.language.id, 'ext': 'snippet.html'},
                CLLD.Map.options.info_query),
            CLLD.Map.options.info_query == undefined ? {} : CLLD.Map.options.info_query,
            function(data, textStatus, jqXHR) {
                _openPopup(layer, data);
            },
            'html'
        );
    }

    var _icon = function(feature, size) {
        return L.icon({
            iconUrl: feature.properties.icon,
            iconSize: [size, size],
            iconAnchor: [Math.floor(size/2), Math.floor(size/2)],
            popupAnchor: [0, 0]
        });
    }

    var _onEachFeature = function(feature, layer) {
        var size = 30;
        if (CLLD.Map.options.sidebar) {
            size = 20;
        }
        layer.setIcon(_icon(feature, size));
        CLLD.Map.oms.addMarker(layer);
        CLLD.Map.marker_map[feature.properties.language.id] = layer;
        layer.bindLabel(feature.properties.language.name);
    };

    var _zoomToExtent = function() {
        if (CLLD.Map.options.center) {
            return;
        }
        var i, pbounds, bounds;
        for (name in CLLD.Map.layer_map) {
            if (CLLD.Map.layer_map.hasOwnProperty(name)) {
                pbounds = CLLD.Map.layer_map[name].getBounds();
                if (pbounds.isValid()) {
                    if (bounds) {
                        bounds.extend(pbounds);
                    } else {
                        bounds = L.latLngBounds(pbounds)
                    }
                }
            }
        }
        if (bounds) {
            CLLD.Map.map.fitBounds(bounds);
        } else {
            CLLD.Map.map.fitWorld();
        }
    };

    var _init = function (eid, layers, options) {
        var i, hash, layer, baseLayers = [
            "OpenStreetMap.Mapnik",
            "OpenStreetMap.BlackAndWhite",
            "Thunderforest.Transport",
            "Thunderforest.Landscape",
            "MapQuestOpen.OSM",
            "MapQuestOpen.Aerial",
            "Stamen.Watercolor",
            "Esri.WorldStreetMap",
            "Esri.DeLorme",
            "Esri.WorldTopoMap",
            "Esri.WorldImagery",
            "Esri.WorldTerrain",
            "Esri.WorldShadedRelief",
            "Esri.WorldPhysical"];
        CLLD.Map.options = options == undefined ? {} : options;
        CLLD.Map.map = L.map(
            eid,
            {center: [5.5, 152.58], scrollWheelZoom: false, maxZoom: 12, fullscreenControl: true});
        CLLD.Map.oms = new OverlappingMarkerSpiderfier(CLLD.Map.map);
        CLLD.Map.oms.addListener('click', _showInfoWindow);

        if (CLLD.Map.options.hash) {
            hash = new L.Hash(CLLD.Map.map);
        }

        L.control.layers.provided(baseLayers, []).addTo(CLLD.Map.map);

        for (name in layers) {
            if (layers.hasOwnProperty(name)) {
                CLLD.Map.layer_map[name] = L.geoJson(undefined, {onEachFeature: _onEachFeature}).addTo(CLLD.Map.map);

                if ($.type(layers[name]) === 'string') {
                    $.getJSON(layers[name], {layer: name}, function(data) {
                        CLLD.Map.layer_map[data.properties.layer].addData(data);
                        _zoomToExtent();
                    });
                } else {
                    CLLD.Map.layer_map[name].addData(layers[name]);
                    _zoomToExtent();
                }
            }
        }
        if (CLLD.Map.options.center) {
            CLLD.Map.map.setView(
                CLLD.Map.options.center,
                CLLD.Map.options.zoom == undefined ? 5 : CLLD.Map.options.zoom);
        } else {
            if (CLLD.Map.map.getZoom() > 5) {
                CLLD.Map.map.setZoom(5);
            }
        }
    }

    return {
        eachMarker: function(func) {
            for (id in CLLD.Map.marker_map) {
                if (CLLD.Map.marker_map.hasOwnProperty(id)) {
                    func(CLLD.Map.marker_map[id]);
                }
            }
        },
        resizeIcons: function(size) {
            size = size === undefined ? $('input[name=iconsize]:checked').val(): size;
            CLLD.Map.eachMarker(function(marker){
                marker.setIcon(_icon(marker.feature, parseInt(size)));
            });
        },
        toggleLabels: function(ctrl){
            var display = $(ctrl).prop('checked');
            CLLD.Map.eachMarker(function(marker){
                if (display) {
                    marker.showLabel();
                } else {
                    marker.hideLabel();
                }
            });
        },
        filterMarkers: function(show){
            CLLD.Map.eachMarker(function(marker){
                if (show(marker)) {
                    marker._icon.style.display = 'block';
                } else {
                    marker._icon.style.display = 'none';
                }
            });
        },
        marker_map: {},
        layer_map: {},
        oms: undefined,
        popup: undefined,
        map: undefined,
        init: _init,
        showInfoWindow: _showInfoWindow,
        toggleLayer: function(layer, ctrl) {
            CLLD.Map.layer_map[layer].eachLayer(function(l){
                l._icon.style.display = $(ctrl).prop('checked') ? 'block' : 'none';
            });
        }
    }
})();
