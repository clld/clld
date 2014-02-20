
The request object
------------------

``clld`` registers a
`custom request factory <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hooks.html#changing-the-request-factory>`_,
i.e. the request object available in view code or templates is an instance of
:py:class:`clld.web.app.ClldRequest`.


.. autoclass:: clld.web.app.ClldRequest
    :members:


Page components
---------------

``clld`` supports page components for web apps (i.e. parts of pages which require HTML
code and JavaScript to define behavior) with the
:py:class:`clld.web.util.component.Component` virtual base class.

.. autoclass:: clld.web.util.component.Component
    :members:

The design rationale for components is the idea to build the bridge between server and
client as cleanly as possible by putting the code to collect options for a client side
object and the instantiation of a these objects into one Python class (plus a mako
template referenced in this class).


DataTables
~~~~~~~~~~

DataTables are implemented as Python classes, providing configuration and server-side
processing for `jquery datatables <http://datatables.net/>`_.

.. autoclass:: clld.web.datatables.base.DataTable
    :members:
    :special-members:


.. autoclass:: clld.web.datatables.base.Col
    :members:


.. _sec-maps:

Maps
~~~~

Maps are implemented as subclasses of :py:class:`clld.web.maps.Map`, providing
configuration and server-side processing for `leaflet maps <http://leafletjs.com>`_.

The process for displaying a map is as follows:

1. In python view code a map object is instantiated and made available to a mako template
   (either via the registry or directly, as template variable).
2. In the mako template, the render method of the map is called, thus inserting HTML
   created from the template ``clld/web/templates/map.mako`` into the page.
3. When the browser renders the page, :js:func:`CLLD.map` is called, instantiating a
   leaflet map object.
4. During initialization of the leaflet map, for each :py:class:`clld.web.maps.Layer` of
   the map a `leaflet geoJson layer <http://leafletjs.com/reference.html#geojson>`_ is
   instantiated, adding data to the map.


.. autoclass:: clld.web.maps.Map
    :members:
    :special-members:

.. autoclass:: clld.web.maps.Layer
    :members:
    :special-members:

.. js:function:: CLLD.map(eid, layers, options)

    :param string eid: DOM element ID for the map object.
    :param array layers: List of layer specifications.
    :param object options: Map options.
    :return: CLLD.Map instance.


Adapters
~~~~~~~~

.. automodule:: clld.web.adapters.base
    :members:


