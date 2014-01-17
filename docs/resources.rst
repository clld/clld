
.. _sec-resource:
Resources
=========

Resources are a central concept in CLLD. While we may use the term resource
also for single instances, more generally a resource is a type of data implementing
an interface to which behaviour can be attached.

The default resources known in a CLLD app are listed in ``clld.RESOURCES``, but it is
possible to extend this list when configuring a custom app.

Resources have the following attributes:

name
    a string naming the resource.

interface
    class specifying the interface the resource implements.

model
    core model class for the resource.

Behaviour may be tied to a resource either via the ``name`` (as is the case for routes) or
via the ``interface`` (as is the case for adapters).


.. _sec-resource-models:
Models
------

Each resource is associated with a db model class and optionally with a custom
db model derived from the default one using joined table inheritance.


.. _sec-resource-adapters:
Adapters
--------

TODO


.. _sec-resource-routes:
Routes
------

The ``clld`` framework uses
`URL dispatch <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/urldispatch.html>`_
to map default views to URLs for resources.

For each resource the following routes and views (and URLs) are registered by default:

- an index view for the route ``<name>s`` and the URL ``/<name>s``,
- an alternative index view for the route ``<name>s_alt`` and the URL pattern ``/<name>s.{ext}``,
- a details view for the route ``<name>`` and the URL pattern ``/<name>s/{id}``,
- an alternative details view for the route ``<name>_alt`` and the URL ``/<name>s/{id}.{ext}``.


.. _sec-resource-views:
Views
-----

clld.web.views

- index
- detail


Providing custom data for a reources details template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since the view rendering a resources details representations is implemented in
clld core code, clld applications may need a way to provide additional context
for the templates. This can be done by implementing an appropriately named
function in the app.util which will be looked up and called in a BeforeRender
event subscriber.
