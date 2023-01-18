
exports.mochaGlobalSetup = async function () {
    this.jsdom = require('jsdom-global')()
    window.jQuery = global.$ = global.jQuery = require('../src/clld/web/static/js/jquery.js');

    /* jsdom doesn't export a complete Option constructor yet. */
    global.Option = function(text, value, defaultSelected, selected) {
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
    require("../src/clld/web/static/js/leaflet-hash.js");
    require("../src/clld/web/static/js/leaflet-providers.js");
    require("../src/clld/web/static/js/select2.js");
};

exports.mochaGlobalTeardown = async function () {
};
