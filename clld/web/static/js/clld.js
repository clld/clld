/**
 * Main JavaScript library for the clld framework.
 * @module clld
 */

/**
 * We define one object which serves as namespace for the package.
 * @namespace
 * @type {{routes: {}, base_url: string, query_params: {}}}
 */
CLLD = {
    'routes': {},
    'base_url': '',
    'query_params': {}
};

/**
 * Create a URL relative to the apps base URL.
 * @param {string} path - path component of the URL.
 * @param {{}} query - dictionary of URL query parameters.
 * @returns {string}
 */
CLLD.url = function(path, query) {
    var url = CLLD.base_url + path,
        sep = '?';

    if (/\?/.test(url)) {
        sep = '&';
    }

    if (query) {
        url += sep + $.param(query);
    }

    return url;
};

/**
 * Create a URL for a route within the app.
 * @param {string} route - route name.
 * @param {{}} data - dictionary providing to data so substitute in the route pattern.
 * @param query
 * @returns {string|*}
 */
CLLD.route_url = function(route, data, query) {
    var key,
        path = CLLD.routes[route];

    for (key in data) {
        if (data.hasOwnProperty(key)) {
            path = path.replace('{'+key+'}', data[key]);
        }
    }

    return CLLD.url(path, query);
};


CLLD.TreeView = (function(){
    return {
        init: function() {
            $('input.treeview').change(function () {
                var icon = $('label[for="'+this.getAttribute('id')+'"]').children('i');
                if (icon && icon.hasClass && icon.hasClass('icon-treeview')) {
                    if ($(this).prop('checked')) {
                        icon.first().addClass('icon-chevron-down');
                        icon.first().removeClass('icon-chevron-right');
                    } else {
                        icon.first().addClass('icon-chevron-right');
                        icon.first().removeClass('icon-chevron-down');
                    }
                }
                return true;
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


CLLD.MultiSelect = (function(){
    return {
        data: function (term, page) {return {q: term, t: 'select2'};},
        results: function (data, page) {return data;},
        addItem: function (eid, obj) {
            var data, s = $('#'+eid);
            data = s.select2('data');
            data.push(obj);
            s.select2('data', data);
        }
    }
})();


CLLD.Feed = (function(){
    var _init = function(spec) {
        var feed = new google.feeds.Feed(spec.url);

        feed.setNumEntries(spec.numEntries == undefined ? 4 : spec.numEntries);
        feed.load(function(result) {
            if (!result.error) {
                var title = spec.title == undefined ? result.feed.title : spec.title;
                //var content = '<h3><a href="'+result.feed.link+'">'+title+'</a></h3>';
                if (spec.linkTitle) {
                    title = '<a href="'+spec.url+'">'+title+'</a>';
                }
                var content = '<h3>'+title+'</h3>';
                for (var j = 0; j < result.feed.entries.length; j++) {
                    var entry = result.feed.entries[j];
                    content += '<h4><a href="'+entry.link+'">'+entry.title+'</a></h4>';
                    content += '<p class="muted"><small>'+entry.publishedDate+'</small></p>';
                    content += '<p>'+entry.contentSnippet+'</p>';
                }
                $('#'+spec.eid).html(content);
            }
        });
    };

    return {
        init: _init
    }
})();


CLLD.Modal = (function(){
    var _show = function(title, url, html) {
        $('#ModalLabel').html(title);
	if (url) {
	    $('#ModalBody').load(url);
	} else {
	    $('#ModalBody').html(html);
	}
        $('#Modal').modal('show');
    };

    return {
        show: _show
    }
})();

/**
 * Dictionary to store references to DataTable objects.
 *
 * @type {{}}
 */
CLLD.DataTables = {};

/**
 * DataTable wraps jquery DataTables objects.
 */
CLLD.DataTable = (function(){

    /**
     * Initialize a DataTable.
     * 
     * @public
     * @name DataTable#init
     * @function
     */    
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

        CLLD.DataTables[eid] = $('#'+eid).dataTable(options);
        $('#'+eid+'_filter').hide();
        if (toolbar) {
            $("."+eid+"-toolbar").html(toolbar);
        }
        //$('#'+eid+' #searchCol').change(function(){CLLD.DataTables[eid].fnFilter($('#'+eid+' .dataTables_filter input').val())});
        $('#'+eid+' tbody td button.details').live('click', function () {
            var nTr = $(this).parents('tr')[0];
            if (CLLD.DataTables[eid].fnIsOpen(nTr)) {
                CLLD.DataTables[eid].fnClose(nTr);
            } else {
                $.get($(this).attr('href'), {}, function(data, textStatus, jqXHR) {
                    CLLD.DataTables[eid].fnOpen(nTr, data, 'details');
                }, 'html');
            }
        });

        $("#"+eid+" tfoot input").keyup( function () {
            /* Filter on the column (the index) of this element */
            CLLD.DataTables[eid].fnFilter(this.value, $("#"+eid+" tfoot .control").index(this));
        });

        $("#"+eid+" tfoot select").change( function () {
            /* Filter on the column (the index) of this element */
            CLLD.DataTables[eid].fnFilter($(this).val(), $("#"+eid+" tfoot .control").index(this));
        });

        var dl = '<p>You may use the download button <i class="icon-download-alt"> </i> to download the currently selected items in various formats.</p>';
        if (options.sDescription) {
            dl += options.sDescription;
        }
        for (i=0; i < options.aoColumns.length; i++) {
            col = options.aoColumns[i];
            if (col.sDescription) {
                dl += '<dt>'+col.sTitle+'</dt><dd>'+col.sDescription+'</dd>';
            }
        }

        $('.'+eid+'-cdOpener').clickover({
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

        for (i=0; i < options.aoColumns.length; i++) {
            col = options.aoColumns[i];
            if (col.sFilter) {
                CLLD.DataTables[eid].fnFilter(col.sFilter, i);
            }
        }
    };

    return {
        init: _init,
        current_url: function(eid, fmt) {
            var url, parts,
                query = {'sEcho': 1},
                oSettings = CLLD.DataTables[eid].fnSettings();
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
            parts[0] = parts[0].replace('.html', '');
            if (parts.length == 1) {
                url = parts[0] + '.' + fmt + '?'
            } else {
                url = parts[0] + '.' + fmt + '?' + parts[1] + '&'
            }
            return url + $.param(query);
        }
    }
})();


CLLD.Maps = {};

CLLD.MapIcons = {
    base: function(feature, size) {
        return L.icon({
            iconUrl: feature.properties.icon,
            iconSize: [size, size],
            iconAnchor: [Math.floor(size/2), Math.floor(size/2)],
            popupAnchor: [0, 0]
        });
    }
};


/**
 * Manager for a leaflet map
 *
 * qw remove the attribution control by default. see
 * https://groups.google.com/d/msg/leaflet-js/fA6M7fbchOs/JTNVhqdc7JcJ
 */
CLLD.Map = function(eid, layers, options) {
    CLLD.Maps[eid] = this;
    this.options = options == undefined ? {} : options;
    this.options.info_query = this.options.info_query == undefined ? {} : this.options.info_query;
    this.options.info_route = this.options.info_route == undefined ? 'language_alt' : this.options.info_route;
    this.map = L.map(
        eid,
        {
            center: [5.5, 152.58],
            scrollWheelZoom: false,
            maxZoom: this.options.max_zoom == undefined ? 6 : this.options.max_zoom,
            fullscreenControl: true,
            attributionControl: false
        }
    );

    var i, hash, layer,
        local_data = false,
        baseLayers = [
        "Thunderforest.Landscape",
        "Thunderforest.Transport",
        "OpenStreetMap.Mapnik",
        "OpenStreetMap.BlackAndWhite",
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

    function _openPopup(layer, html) {
        var map = CLLD.Maps[eid];
        if (!map.popup) {
            map.popup = L.popup();
        }
        map.popup.setLatLng(layer.getLatLng());
        map.popup.setContent(html);
        map.map.openPopup(map.popup);
    }

    this.showInfoWindow = function(layer) {
        var map = CLLD.Maps[eid];

        if (map.options.no_popup) {
            if (!map.options.no_link) {
                document.location.href = CLLD.route_url(
                    'language', {'id': layer.feature.properties.language.id});
            }
            return;
        }

        if (map.marker_map.hasOwnProperty(layer)) {
            // allow opening the info window by language id
            layer = map.marker_map[layer];
        }
        if (layer.feature.properties.popup) {
            _openPopup(layer, layer.feature.properties.popup);
        } else {
            $.get(
                CLLD.route_url(
                    map.options.info_route,
                    {'id': layer.feature.properties.language.id, 'ext': 'snippet.html'},
                    $.extend(
                        {},
                        CLLD.query_params,
                        map.options.info_query,
                        layer.feature.properties.info_query == undefined ? {} : layer.feature.properties.info_query)),
                map.options.info_query,
                function(data, textStatus, jqXHR) {
                    _openPopup(layer, data);
                },
                'html'
            );
        }
    };

    this.icon = CLLD.MapIcons[this.options.icons == undefined ? 'base' : this.options.icons];

    var _onEachFeature = function(feature, layer) {
        var size = 30,
            map = CLLD.Maps[eid];
        if (feature.properties.icon_size) {
            size = feature.properties.icon_size;
        } else if (map.options.sidebar) {
            size = 20;
        } else if (map.options.icon_size) {
            size = map.options.icon_size;
        }
        layer.setIcon(map.icon(feature, size));
        if (feature.properties.zindex) {
            layer.setZIndexOffset(feature.properties.zindex);
        }
        map.oms.addMarker(layer);
        map.marker_map[feature.properties.language.id] = layer;
        layer.bindLabel(feature.properties.label == undefined ? feature.properties.language.name : feature.properties.label);
    };

    var _zoomToExtent = function() {
        var map = CLLD.Maps[eid];
        if (map.options.center) {
            return;
        }
        var i, pbounds, bounds;
        for (name in map.layer_map) {
            if (map.layer_map.hasOwnProperty(name)) {
                pbounds = map.layer_map[name].getBounds();
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
            map.map.fitBounds(bounds);
        } else {
            map.map.fitWorld();
        }
    };

    this.oms = new OverlappingMarkerSpiderfier(this.map);
    this.oms.addListener('click', this.showInfoWindow);

    if (this.options.hash) {
        hash = new L.Hash(this.map);
    }

    L.control.layers.provided(baseLayers, []).addTo(this.map);

    this.marker_map = {};
    this.layer_map = {};
    this.layer_geojson = {};

    this.eachMarker = function(func) {
        for (id in this.marker_map) {
            if (this.marker_map.hasOwnProperty(id)) {
                func(this.marker_map[id]);
            }
        }
    };

    for (name in layers) {
        if (layers.hasOwnProperty(name)) {
            this.layer_map[name] = L.geoJson(undefined, {onEachFeature: _onEachFeature}).addTo(this.map);
            this.layer_geojson[name] = layers[name];

            if ($.type(layers[name]) === 'string') {
                $.getJSON(layers[name], {layer: name}, function(data) {
                    var map = CLLD.Maps[eid];
                    map.layer_map[data.properties.layer].addData(data);
                    _zoomToExtent();
                    if (map.options.show_labels) {
                        map.eachMarker(function(marker){marker.showLabel()})
                    }
                });
            } else {
                local_data = true;
                this.layer_map[name].addData(layers[name]);
            }
        }
    }

    if (local_data) {
        _zoomToExtent();
        if (this.options.show_labels) {
            this.eachMarker(function(marker){marker.showLabel()})
        }
    }

    if (this.options.center) {
        this.map.setView(
            this.options.center,
            this.options.zoom == undefined ? 5 : this.options.zoom);
    }

    if (this.options.on_init) {
        this.options.on_init(this);
    }
};

CLLD.map = function(eid, layers, options) {
    return new CLLD.Map(eid, layers, options);
};

CLLD.mapToggleLabels = function(eid, ctrl){
    var display = $(ctrl).prop('checked'),
        map = CLLD.Maps[eid];
    map.eachMarker(function(marker){
        if (display && marker._icon.style.display != 'none') {
            marker.showLabel();
        } else {
            marker.hideLabel();
        }
    });
};

CLLD.mapGetMap = function(eid) {
    if (!eid) {
        for (eid in CLLD.Maps) {
            return CLLD.Maps[eid];
        }
    } else {
        return CLLD.Maps[eid];
    }
    return undefined;
};

CLLD.mapShowInfoWindow = function(eid, layer) {
    var map = CLLD.mapGetMap(eid);
    map.showInfoWindow(layer);
};

CLLD.mapResizeIcons = function(eid, size) {
    var hidden, map = CLLD.Maps[eid];
    size = size === undefined ? $('input[name=iconsize]:checked').val(): size;
    map.eachMarker(function(marker){
        hidden = marker._icon.style.display == 'none';
        marker.setIcon(map.icon(marker.feature, parseInt(size)));
        if (hidden) {
            marker._icon.style.display = 'none';
        }
    });
};

CLLD.mapFilterMarkers = function(eid, show){
    var map = CLLD.Maps[eid],
        show_label = $('#map-label-visiblity').prop('checked');
    map.eachMarker(function(marker){
        if (show(marker)) {
            marker._icon.style.display = 'block';
            if (show_label) {
                marker.showLabel();
            }
        } else {
            marker._icon.style.display = 'none';
            marker.hideLabel();
        }
    });
};

CLLD.mapToggleLayer = function(eid, layer, ctrl) {
    var map = CLLD.Maps[eid];
    map.layer_map[layer].eachLayer(function(l){
        l._icon.style.display = $(ctrl).prop('checked') ? 'block' : 'none';
    });
};

CLLD.mapShowGeojson = function(eid, layer) {
    var map = CLLD.Maps[eid],
        data = map.layer_geojson[layer];

    if ($.type(data) === 'string') {
        $.getJSON(data, {layer: layer}, function(_data) {
            CLLD.Modal.show('<a href="' + data + '">' + _data.properties.name + '</a>', null, '<pre>' + JSON.stringify(_data, null, 2) + '</pre>');
        });
    } else {
        CLLD.Modal.show(data.properties.name, null, '<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    }
    return false;
};

/*
 * callback called when call to gbs dynamic links API returns.
 * see https://developers.google.com/books/docs/dynamic-links
 */
CLLD.process_gbs_info = function(booksInfo) {
    var target, info, id_;

    for (id_ in booksInfo) {
        if (booksInfo.hasOwnProperty(id_)) {
            target = $('#' + id_.replace(':', '-'));
            info = booksInfo[id_];

            if (info.preview == "full" || info.preview == "partial") {
                target.after('<div><a title="preview at Google Books" href="' + info.preview_url + '"><img src="https://www.google.com/intl/en/googlebooks/images/gbs_preview_button1.gif"/></a></div>');
            } else {
                target.after('<div><a title="info at Google Books" href="' + info.info_url + '"><i class="icon-share"> </i> info at Google Books</a></div>');
            }
            if (info.thumbnail_url) {
                target.before('<div style="float: right;"><a title="info at Google Books" href="' + info.info_url + '"><img class="gbs-thumbnail" src="' + info.thumbnail_url + '"/></a></div>');
            }
            target.show();
        }
    }
};
