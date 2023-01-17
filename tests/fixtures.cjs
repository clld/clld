

exports.mochaGlobalSetup = async function () {
    this.jsdom = require('jsdom-global')()
    window.jQuery = global.$ = global.jQuery = require('../src/clld/web/static/js/jquery.js');

    const webIDLConversions = require("webidl-conversions");

    global.Option = function(text, value, defaultSelected, selected) {
        if (text === undefined) {
            text = "";
        }
        text = webIDLConversions.DOMString(text);

        if (value !== undefined) {
            value = webIDLConversions.DOMString(value);
        }

        defaultSelected = webIDLConversions.boolean(defaultSelected);
        selected = webIDLConversions.boolean(selected);
        return window._document.createElement("option");
    }
    Object.defineProperty(Option, "prototype", {
        value: window.HTMLOptionElement.prototype,
        configurable: false,
        enumerable: false,
        writable: false
    });
    Object.defineProperty(window, "Option", {
        value: Option,
        configurable: true,
        enumerable: false,
        writable: true
    });

    require("../src/clld/web/static/js/bootstrap.js");
    require("../src/clld/web/static/js/bootstrap-slider.js");
    require("../src/clld/web/static/js/bootstrapx-clickover.js");
    require("../src/clld/web/static/js/intro.min.js");
    require("../src/clld/web/static/js/jquery.dataTables.js")(window, $);
    global.L = require("../src/clld/web/static/js/leaflet.js");
    require("../src/clld/web/static/js/L.Control.Resizer.js");
    //"src/clld/web/static/js/Leaflet.fullscreen.js",
    require("../src/clld/web/static/js/leaflet-hash.js");
    require("../src/clld/web/static/js/leaflet-providers.js");
    //const oms = require("../src/clld/web/static/js/oms.min.js");
    //global.OverlappingMarkerSpiderfier = oms.OverlappingMarkerSpiderfier;
    //"src/clld/web/static/js/raphael.min.js",
    require("../src/clld/web/static/js/select2.js");
    //require("../src/clld/web/static/js/tree.jquery.js")(window);

  //this.server = await startSomeServer({port: process.env.TEST_PORT});
  //console.log(`server running on port ${this.server.port}`);
};

exports.mochaGlobalTeardown = async function () {
  //await this.server.stop();
  //console.log('server stopped!');
};
