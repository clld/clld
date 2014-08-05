Test = TestCase("CLLD");
fcalled = false;

Test.prototype.test_url = function() {
    assertEquals(
        '/path?p1=a&p2=b',
        CLLD.url('/path?p1=a', {'p2': 'b'}));
};

Test.prototype.test_route_url = function() {
    CLLD.routes.language = '/language/{id}';
    assertEquals(
        '/language/1?format=bib',
        CLLD.route_url('language', {id: 1}, {format: 'bib'}));
};

Test.prototype.test_Feed = function() {
    CLLD.Feed.init({url: 'http://blog.wals.info', linkTitle: 't'});
};

Test.prototype.test_TreeView = function() {
    /*:DOC += <label for="tv"><i class="icon-treeview"> </i><input id="tv" class="treeview" type="checkbox"/></label> */
    CLLD.TreeView.init();
    CLLD.TreeView.show(1);
    CLLD.TreeView.hide(1);
    $('input.treeview').delay(100).trigger('click');
    $('input.treeview').delay(100).trigger('click');
};

Test.prototype.test_MultiSelect = function() {
    /*:DOC += <div id="ms"/> */
    CLLD.MultiSelect.addItem('ms', {'text': 't', 'id': 1});
    CLLD.MultiSelect.data('ms');
    CLLD.MultiSelect.results('ms');
};

Test.prototype.test_DataTable = function() {
    /*:DOC += <table id="dt"><thead><tr><th>1</th><th>2</th></tr></thead><tbody></tbody><tfoot><tr><input type="text" class="control"/></tr></tfoot></table> */
    CLLD.DataTable.init(
        'dt',
        '<p/>',
        {
            'sDescription': '<p>the table</p>',
            'iDisplayLength': 10,
            'sPaginationType': 'bootstrap',
            'sAjaxSource': '/test/clld/tests/xhr/dt.json',
            'aoColumns': [
                {sName: 'P2', sDescription: 'the col', sFilter: 'Aus'},
                {sName: 'P2'}],
            'aoPresearchCols': [{sSearch: 'Aus'}]
        });
    CLLD.DataTable.current_url('dt');
    $('tfoot input').delay(100).trigger('keyup');
    $('div.pagination li.next a').delay(100).trigger('click');
    $('#bt').delay(100).trigger('click');
};

Test.prototype.test_MapWithRemoteData = function() {
    /*:DOC += <div id="map"/><div id="map2"/> <div id="map3"/>  */
    var layer = {feature: {properties: {language: {id: '1'}}}},
        url = '/test/clld/tests/xhr/languages.json';

    CLLD.Maps = {};
    assertEquals(undefined, CLLD.mapGetMap());
    CLLD.map(
        'map',
        {l: url},
        {center: [5.5, 5.5], no_popup: true, no_link: true, show_labels: true});
    CLLD.mapShowGeojson('map', 'l');
    assertEquals(undefined, CLLD.mapGetMap('mmm'));
    assertEquals(CLLD.mapGetMap('map'), CLLD.mapGetMap());
    CLLD.mapShowInfoWindow('map', layer);
    CLLD.map('map2', {l1: url}, {sidebar: true});
    CLLD.map('map3', {l1: url}, {icon_size: 15});
};

Test.prototype.test_MapWithLocalData = function() {
    /*:DOC += <div id="map"/><input type="checkbox" id="unchecked" />  <input type="checkbox" id="cb" checked="checked" /> <input type="checkbox" checked="checked" id="map-label-visiblity"/> */
    var fc = {
        "type": "FeatureCollection",
        "properties": {"layer": ""},
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
                    icon: "http://apics-online.info/clld-static/icons/cff6600.png"}
            }
        ]
        },
        on_init = function() {fcalled = true;};

    CLLD.routes['test_info_route'] = '/test/clld/tests/xhr/language{id}.{ext}';

    CLLD.map(
        'map',
        {l1: fc},
        {hash: true, show_labels: true, on_init: on_init, info_route: 'test_info_route'});
    assertTrue(fcalled);
    fcalled = false;
    CLLD.mapShowInfoWindow('map', '1');
    CLLD.mapFilterMarkers('map', function(m){return true;});
    CLLD.mapFilterMarkers('map', function(m){return false;});
    CLLD.mapShowGeojson('map', 'l1');
    CLLD.mapToggleLabels('map', '#cb');
    CLLD.mapToggleLabels('map', '#cb');
    CLLD.mapToggleLabels('map', '#unchecked');
    CLLD.mapResizeIcons('map', 15);
    CLLD.mapToggleLayer('map', 'l1', '#cb');
    CLLD.mapLegendFilter('map', 'name', 'jsname', function(p){return 'a'}, 'dt');
};

Test.prototype.test_process_gbs_info = function() {
    /*:DOC += <div id="id1"/> */
    CLLD.process_gbs_info({id1: {preview: 'full', preview_url: '', thumbnail_url: 'u'}});
    CLLD.process_gbs_info({id1: {preview: '', preview_url: '', info_url: ''}});
};

Test.prototype.test_Modal = function() {
    /*:DOC += <div id="Modal"><div id="ModalLabel"></div><div id="ModalBody"></div></div> */
    assertEquals($('#ModalLabel').html(), '');
    CLLD.Modal.show('The Title', '/test/clld/tests/xhr/language1.snippet.html');
    assertEquals($('#ModalLabel').html(), 'The Title');
    CLLD.Modal.show('Title', null, '<h1>Title</h1>');
};
