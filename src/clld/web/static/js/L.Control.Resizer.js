'use strict';

(function(L) {
    if (typeof L === 'undefined') {
        throw new Error('Leaflet must be included first');
    }

    L.Control.Resizer = L.Control.extend({
        options: {
            direction: 'e',  // valid values e, s, se
            onlyOnHover: false,
            updateAlways: true,
            pan:false,
        },

        _END: {
            mousedown: 'mouseup',
            touchstart: 'touchend',
            pointerdown: 'touchend',
            MSPointerDown: 'touchend'
        },

        _MOVE: {
            mousedown: 'mousemove',
            touchstart: 'touchmove',
            pointerdown: 'touchmove',
            MSPointerDown: 'touchmove'
        },

        initialize: function(options) {
            L.Util.setOptions(this, options);
            this._initialOffsetX = 0;
            this._initialOffsetY = 0;
            this.options.position = 'leaflet-control-resizer-corner-' + this.options.direction;
            this.enable();
        },

        enable: function() {
            this._enabled = true;
            return this;
        },

        disable: function() {
            this._enabled = false;
            return this;
        },

        onAdd: function (map) {
            this._prepareLocation(map);

            var className = 'leaflet-control-resizer';
            var classNameTransp = className + (this.options.onlyOnHover ? '-transparent' : '-opaque');
            var classNameLoc = className + '-' + this.options.direction;
            this._container = L.DomUtil.create('div',
                                               className + ' ' + classNameTransp + ' ' + classNameLoc,
                                               map.getContainer());
            var container = this._container;

            L.DomEvent.on(container, 'mousedown mouseup click touchstart drag', L.DomEvent.stopPropagation);

            /* IE11 seems to process events in the wrong order, so the only way to prevent map movement while dragging the
             * slider is to disable map dragging when the cursor enters the slider (by the time the mousedown event fires
             * it's too late becuase the event seems to go to the map first, which results in any subsequent motion
             * resulting in map movement even after map.dragging.disable() is called.
             */
            /*
            L.DomEvent.on(container, 'mouseenter', function (e) { map.dragging.disable(); });
            L.DomEvent.on(container, 'mouseleave', function (e) { map.dragging.enable(); });
            */

            L.DomEvent.on(container, 'mousedown touchstart', this._initResize, this);

            return this._container;
        },

        onRemove: function(map) {
            L.DomEvent.off(this._container, 'mousedown touchstart', this._initResize, this);
            L.DomEvent.off(this._container, 'mousedown mouseup click touchstart drag', L.DomEvent.stopPropagation);
        },

        fakeHover: function(ms) {
            var className = 'leaflet-control-resizer-transparent-fakedhover';
            var cont = this._container;
            L.DomUtil.addClass(cont, className);
            setTimeout(function() { L.DomUtil.removeClass(cont, className); }, ms | 1000);
        },

        _prepareLocation: function(map) {
            var corners = map._controlCorners;
            var l = 'leaflet-control-resizer-corner-' + this.options.direction;
            var container = map._controlContainer;

            corners[l] = L.DomUtil.create('div', l, container);
        },

        _initResize: function (e) {
            if (e._simulated || !this._enabled) { return; }

            if (this._started) return;
            this._started = true;
            this._moved = false;

            var first = (e.touches && e.touches.length === 1 ? e.touches[0] : e)

            L.DomUtil.disableImageDrag();
            L.DomUtil.disableTextSelection();

            this.fire('down', e);

            var mapCont = this._map.getContainer();
            this._initialOffsetX = mapCont.offsetWidth + mapCont.offsetLeft - first.clientX;
            this._initialOffsetY = mapCont.offsetHeight + mapCont.offsetTop - first.clientY;

            L.DomEvent.on(document, this._END[e.type], this._stopResizing, this);
            L.DomEvent.on(this._container, this._END[e.type], this._stopResizing, this);

            L.DomEvent.on(document, this._MOVE[e.type], this._duringResizing, this);
        },

        _duringResizing: function (e) {
            if (e._simulated) { return; }

            var first = (e.touches && e.touches.length === 1 ? e.touches[0] : e)

            L.DomEvent.preventDefault(e);

            if (!this._moved) {
                this.fire('dragstart', e);
            }
            this.fire('predrag', e);

            var mapCont = this._map.getContainer();
            if (this.options.direction.indexOf('e') >=0) {
                mapCont.style.width = (first.clientX - mapCont.offsetLeft + this._initialOffsetX) + 'px';
                this._moved = true;
            }
            if (this.options.direction.indexOf('s') >=0) {
                mapCont.style.height = (first.clientY - mapCont.offsetTop + this._initialOffsetY) + 'px';
                this._moved = true;
            }
            this._moved = true;

            if (this.options.updateAlways) {
                this._map.invalidateSize({ pan: this.options.pan });
            }

            this.fire('drag', e);
        },

        _stopResizing: function(e) {
            if (e._simulated) { return; }

            for (var i in this._MOVE)
            {
                L.DomEvent.off(document, this._MOVE[i], this._duringResizing, this);

                L.DomEvent.off(document, this._END[i], this._stopResizing, this);
                L.DomEvent.off(this._container, this._END[i], this._stopResizing, this);
            }

            this._map.invalidateSize({ pan: this.options.pan });

            L.DomUtil.enableImageDrag();
            L.DomUtil.enableTextSelection();
            this._started = false;
            this.fire('dragend', e);
        }

    });

    L.Control.Resizer.include(L.Evented.prototype);

    L.control.resizer = function (options) {
        return new L.Control.Resizer(options);
    };
})(L);
