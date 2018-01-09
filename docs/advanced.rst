
Advanced configuration
----------------------

This chapter describes somewhat more advanced techniques to configure a ``clld`` app.


Custom map icons
~~~~~~~~~~~~~~~~

``clld`` uses `leaflet <http://leafletjs.com/>`_ to display maps. Thus, techniques to use
custom map markers are based on
`corresponding <http://leafletjs.com/examples/custom-icons/>`_
`mechanisms <https://gist.github.com/comp615/2288108>`_
for leaflet.

Using custom leaflet markers with ``clld`` requires the following steps:

1. Define a javascript function in your app's ``project.js`` which can be used as marker
   factory; the signature of this function must be as follows:

.. js:function:: MYAPP.icon_factory(feature, size)

   :param feature: GeoJSON `feature object <http://geojson.org/geojson-spec.html#feature-objects>`_.
   :param size: Size in pixels of the marker.
   :returns: L.Icon instance.

2. Make this function available to ``clld`` by assigning it to a name in ``CLLD.MapIcons``:

.. code-block:: javascript

    CLLD.MapIcons['myname'] = MYAPP.icon_factory;

3. Configure a map to use the custom icons:

.. code-block:: python

    class MyMap(clld.web.maps.Map):
        def get_options(self):
            return {
                'icons': 'myname',
            }

The name passed as map options will be used to look up the function. This function will
be called for each feature object encountered in the GeoJSON object defining a map's
content, i.e. if you want to use special properties of a language or a parameter value
in your algorithm to compute the appropriate marker, you will probably have to define a
custom GeoJSON adapter for the map as well (see :ref:`sec-geojson`).

A full example to create custom icons which display a number on top of a standard icon
could look as follows:

1. In ``myapp/static/project.js`` add

.. code-block:: javascript

    MYAPP.NumberedDivIcon = L.Icon.extend({
        options: {
            number: '',
            className: 'my-div-icon'
        },
        createIcon: function () {
            var div = document.createElement('div');
            var img = this._createImg(this.options['iconUrl']);
            $(img).width(this.options['iconSize'][0]).height(this.options['iconSize'][1]);
            var numdiv = document.createElement('div');
            numdiv.setAttribute ( "class", "number" );
            $(numdiv).css({
                top: -this.options['iconSize'][0].toString() + 'px',
                left: 0 + 'px',
                'font-size': '12px'
            });
            numdiv.innerHTML = this.options['number'] || '';
            div.appendChild (img);
            div.appendChild (numdiv);
            this._setIconStyles(div, 'icon');
            return div;
        }
    });

    CLLD.MapIcons['numbered'] = function(feature, size) {
        return new MYAPP.NumberedDivIcon({
            iconUrl: url == feature.properties.icon,
            iconSize: [size, size],
            iconAnchor: [Math.floor(size/2), Math.floor(size/2)],
            popupAnchor: [0, 0],
            number: feature.properties.number
        });
    }


2. In ``myapp/static/project.css`` add

.. code-block:: css

    .my-div-icon {
        background: transparent;
        border: none;
    }

    .leaflet-marker-icon .number{
        position: relative;
        font-weight: bold;
        text-align: center;
        vertical-align: middle;
    }
