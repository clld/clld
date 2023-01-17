const expect = require('chai').expect;
const sinon = require('sinon');

var assert = require('assert');
require("../src/clld/web/static/js/clld");


describe('url', function () {
    it('', function () {
        assert.equal(CLLD.url('/path?p1=a', {'p2': 'b'}), '/path?p1=a&p2=b');
    });
});


describe('reload', function () {
    it('', function () {
        CLLD.reload({'x': 'y'}, 'http://localhost');
    });
});

describe('Feed', function () {
    before(function () {
        document.body.innerHTML = '<div id="feed"></div>';
        sinon.stub($, 'get').callsFake(function (url, opts, callback) {
            callback('<?xml version="1.0" encoding="utf-8"?>\
<feed xmlns="http://www.w3.org/2005/Atom">\
  <title>Example Feed</title>\
  <link href="http://example.org/"/>\
  <updated>2003-12-13T18:30:02Z</updated>\
  <author>\
    <name>John Doe</name>\
  </author>\
  <id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>\
  <entry>\
    <title>Atom-Powered Robots Run Amok</title>\
    <link href="http://example.org/2003/12/13/atom03"/>\
    <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>\
    <updated>2003-12-13T18:30:02Z</updated>\
    <summary>Some text.</summary>\
  </entry>\
</feed>');
        });
    });
    after(function () {
        $.get.restore();
    });
    it('', function () {
        CLLD.Feed.init({url: 'feed.xml', title: 'the feed', linkTitle: 't', eid: 'feed'});
        expect(document.getElementById('feed').innerHTML).contain('Robots Run Amok');
    });
});

describe('route_url', function () {
    it('', function () {
        CLLD.routes.language = '/language/{id}';
        assert.equal(
            '/language/1?format=bib',
            CLLD.route_url('language', {id: 1}, {format: 'bib'}));
    });
});

describe('TreeView', function () {
    before(function () {
        document.body.innerHTML = '<label for="tv"><i class="icon-treeview"> </i><input id="tv" class="treeview" type="checkbox"/></label>';
    });
    it('', function () {
        CLLD.TreeView.init();
        CLLD.TreeView.show(1);
        CLLD.TreeView.hide(1);
        $('input.treeview').delay(100).trigger('click');
        $('input.treeview').delay(100).trigger('click');
    });
});

describe('MultiSelect', function () {
    before(function () {
        document.body.innerHTML = '<div id="ms"/>';
    });
    it('', function () {
        CLLD.MultiSelect.addItem('ms', {'text': 't', 'id': 1});
        CLLD.MultiSelect.data('ms');
        CLLD.MultiSelect.results('ms');
    });
});

describe('DataTable', function () {
    before(function () {
        document.body.innerHTML = '<table id="dt"><thead><tr><th>1</th><th>2</th></tr></thead><tbody></tbody><tfoot><tr><input type="text" class="control"/></tr></tfoot></table>';
        sinon.stub($, 'get').callsFake(function (url, opts, callback) {
            callback(
                {
                    "iTotalRecords": 2679,
                    "aaData": [
                        ["Australia & Oceania", "<button id=\"bt\" class=\"details\" href=\"/test/clld/tests/xhr/language1.snippet.html\"/>"],
                        ["Australia & Oceania", ""],
                        ["Australia & Oceania", ""],
                        ["Australia & Oceania", ""],
                        ["Australia & Oceania", ""],
                        ["Australia & Oceania", ""],
                        ["Australia & Oceania", ""],
                        ["Australia & Oceania", ""],
                        ["Australia & Oceania", ""],
                        ["Australia & Oceania", ""],
                        ["Australia & Oceania", ""],
                        ["Australia & Oceania", ""]
                    ],
                    "sEcho": "4",
                    "iTotalDisplayRecords": 12
                }
            );
        });
    });
    after(function () {
        $.get.restore();
    });

    it('', function () {
        CLLD.DataTable.init(
            'dt',
            '<p/>',
            {
                'sDescription': '<p>the table</p>',
                'iDisplayLength': 10,
                'sPaginationType': 'bootstrap',
                'sAjaxSource': 'dt.json',
                'aoColumns': [
                    {sName: 'P2', sDescription: 'the col', sFilter: 'Aus'},
                    {sName: 'P2'}],
                'aoPresearchCols': [{sSearch: 'Aus'}]
            });
        CLLD.DataTable.current_url('dt');
        $('tfoot input').delay(100).trigger('keyup');
        $('div.pagination li.next a').delay(100).trigger('click');
        $('#bt').delay(100).trigger('click');
    });
});

describe('MapWithRemoteData', function () {
    before(function () {
        document.body.innerHTML = '<div id="map"/><div id="map2"/> <div id="map3"/>';
        sinon.stub($, 'getJSON').callsFake(function (url, opts, callback) {
            callback(
                {
                    "type": "FeatureCollection",
                    "properties": {"layer": "l"},
                    "features": [
                        {
                            "geometry": {"type": "Point", "coordinates": [-55.6, 5.833333]},
                            "type": "Feature",
                            "properties": {
                                "language": {
                                    "region": "Caribbean",
                                    "active": true,
                                    "version": 1,
                                    "longitude": -55.6,
                                    "latitude": 5.833333,
                                    "pk": 1,
                                    "id": "1",
                                    "lexifier": "English",
                                    "name": "Early Sranan"
                                },
                                "icon": "http://apics-online.info/clld-static/icons/cff6600.png"
                            }
                        }
                    ]
                }
            );
        });
    });
    after(function () {
        $.getJSON.restore();
    });

    it('', function () {
        var layer = {feature: {properties: {language: {id: '1'}}}},
            url = 'languages.json';

        CLLD.Maps = {};
        assert.equal(undefined, CLLD.mapGetMap());
        CLLD.map(
            'map',
            {l: url},
            {center: [5.5, 5.5], no_popup: true, no_link: true, show_labels: true});
        CLLD.mapShowGeojson('map', 'l');
        assert.equal(undefined, CLLD.mapGetMap('mmm'));
        assert.equal(CLLD.mapGetMap('map'), CLLD.mapGetMap());
        CLLD.mapShowInfoWindow('map', layer);
        CLLD.map('map2', {l: url}, {sidebar: true, zoom: 3});
        CLLD.map('map3', {l: url}, {icon_size: 15});
    });
});

describe('MapWithLocalData', function () {
    before(function () {
        document.body.innerHTML = '<div id="map"/><input type="checkbox" id="unchecked" />  <input type="checkbox" id="cb" checked="checked" /> <input type="checkbox" checked="checked" id="map-label-visiblity"/>';
        sinon.stub($, 'get').callsFake(function (url, opts, callback) {
            callback("<p>Test</p>");
        });
        sinon.stub($, 'ajax').callsFake(function (opts) {
            opts.success("<p>Test</p>");
        });
    });
    after(function () {
        $.get.restore();
        $.ajax.restore();
    });
    it('', function () {
        var fc = {
                "type": "FeatureCollection",
                "properties": {"layer": "l1"},
                "features": [
                    {
                        "geometry": {"type": "Point", "coordinates": [-55.6, 5.833333]},
                        "type": "Feature",
                        "properties": {
                            "language": {
                                "region": "Caribbean",
                                "active": true,
                                "version": 1,
                                "longitude": -55.6,
                                "latitude": 5.833333,
                                "pk": 1,
                                "id": "1",
                                "lexifier": "English",
                                "name": "Early Sranan"
                            },
                            icon_size: 15,
                            zindex: 1000,
                            icon: "http://apics-online.info/clld-static/icons/cff6600.png"
                        }
                    }
                ]
            },
            fcalled = false,
            on_init = function (themap) {
                fcalled = true;
            };
        CLLD.Maps = {};
        CLLD.routes['test_info_route'] = '/test/tests/xhr/language{id}.{ext}';
        CLLD.LayerOptions['l1'] = {x: 1};
        CLLD.map(
            'map',
            {l1: fc},
            {
                //hash: true,
                show_labels: true,
                on_init: on_init,
                resize_direction: 's',
                with_audioplayer: true,
                add_layers_to_control: true,
                info_route: 'test_info_route'
            });
        expect(fcalled).to.be.true;
        $('.leaflet-control-audioplayer-play').delay(100).trigger('click');
        $('.leaflet-control-audioplayer-play').delay(100).trigger('click');
        $('.leaflet-control-audioplayer-stop').delay(100).trigger('click');
        fcalled = false;
        CLLD.mapShowInfoWindow('map', '1');
        CLLD.mapFilterMarkers('map', function (m) {
            return true;
        });
        CLLD.mapFilterMarkers('map', function (m) {
            return false;
        });
        CLLD.mapShowGeojson('map', 'l1');
        CLLD.mapToggleLabels('map', '#cb');
        CLLD.mapToggleLabels('map', '#cb');
        CLLD.mapToggleLanguages('map');
        CLLD.mapToggleLabels('map', '#unchecked');
        CLLD.mapResizeIcons('map', 15);
        CLLD.mapToggleLayer('map', 'l1', '#cb');
        CLLD.mapLegendFilter('map', 'name', 'jsname', function (p) {
            return 'a'
        }, 'dt');
        CLLD.AudioPlayerOptions.test = true;
        CLLD.AudioPlayer.play();
        CLLD.AudioPlayer.stop();
        $('.leaflet-control-audioplayer-play').click();
    });
});

describe('process_gbs_info', function () {
    before(function () {
        document.body.innerHTML = ' <div id="id1"/>';
    });
    it('', function () {
        CLLD.process_gbs_info({id1: {preview: 'full', preview_url: '', thumbnail_url: 'u'}});
        CLLD.process_gbs_info({id1: {preview: '', preview_url: '', info_url: ''}});
    });
});

describe('Modal', function () {
    before(function () {
        document.body.innerHTML = '<div id="Modal"><div id="ModalLabel"></div><div id="ModalBody"></div></div>';
    });
    it('', function () {
        assert.equal($('#ModalLabel').html(), '');
        CLLD.Modal.show('The Title', '/test/tests/xhr/language1.snippet.html');
        assert.equal($('#ModalLabel').html(), 'The Title');
        CLLD.Modal.show('Title', null, '<h1>Title</h1>');
    });
});
