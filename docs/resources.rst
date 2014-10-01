
.. _sec-resource:

Resources
=========

Resources are a central concept in ``clld``. While we may use the term resource
also for single instances, more generally a resource is a type of data implementing
an interface to which behaviour can be attached.

The default resources known in a ``clld`` app are listed in ``clld.RESOURCES``, but it is
possible to extend this list when configuring a custom app (see :ref:`sec-extending-resource`).

Resources have the following attributes:

name
    a string naming the resource.

interface
    class specifying the interface the resource implements.

model
    core model class for the resource.

Behaviour may be tied to a resource either via the ``name`` (as is the case for :ref:`sec-resource-routes`) or
via the ``interface`` (as is the case for :ref:`sec-resource-adapters`).


.. _sec-resource-models:

Models
------

Each resource is associated with a db model class and optionally with a custom
db model derived from the default one using joined table inheritance.


.. _sec-resource-adapters:

Adapters
--------

Adapters are basically used to provide representations of a resource. Thus, if we want to
provide the classification tree of a Glottolog languoid in newick format, we have to write
and register an adapter. This kind of adapter is generally implemented as subclass of
:py:class:`clld.web.adapters.base.Representation` or :py:class:`clld.web.adapters.base.Index`.

For the builtin resources a couple of adapters are registered by default:

- a template-based adapter to render the details page,
- a JSON representation of the resource (based on :py:class:`clld.web.adapters.base.JSON`).
- a CSV representation of a resource index (:py:class:`clld.web.adapters.csv.CsvAdapter`).


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

We distinguish two classes of views for resources:

- index views, implemented in :py:func:`clld.web.views.index_view`, serve rendered adapters
  registered for the interface ``IIndex`` and a particular resource. They typically require
  a corresponding ``DataTable`` subclass to be instantiated as context object when the view
  is executed.
- detail views, implemented in :py:func:`clld.web.views.detail_view`, serve rendered adapters
  registered for the interface ``IRepresentation`` and a particular resource. The resource
  instance with the ``id`` passed in the request will be fetched from the database as context object
  of the view.

.. _sec-resource-templates:

Templates
---------

The adapters associated with resources may use templates to render the response. In particular
this is the case for the HTML index and detail view.



Providing custom data for a reources details template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since the view rendering a resources details representations is implemented in
clld core code, clld applications may need a way to provide additional context
for the templates. This can be done by implementing an appropriately named
function in the app.util which will be looked up and called in a BeforeRender
event subscriber.


.. _sec-resource-request:

Requesting a resource
---------------------

The flow of events when a resource is requested from a ``clld`` app is as follows
(we don't give a complete rundown but only highlight the deviations from the general
`pyramid request processing <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/router.html>`_ flow):

1. When a route for a resource matches, the corresponding factory function is called to
   obtain the context of the request. For index routes this context object is an instance
   of a DataTable, for a details route this is an instance of the resource's model class
   (or a custom specialization of this model).

2. For index routes :py:func:`clld.web.views.index_view` is called, for details routes
   :py:func:`clld.web.views.resource_view`.

3. Both of these look up the appropriate adapter registered for the context, instantiate it
   and call its ``render_to_response`` method. The result of this call is returned as
   ``Response``.

4. If this method uses a `standard template renderer <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/templates.html>`_
   the listener for the ``BeforeRender`` event will look for a function in ``myapp.util``
   with a name of ``<resource_name>_<template_basename>``, e.g. ``dataset_detail_html`` for
   the template ``templates/dataset/detail_html.mako``. If such a function exists, it will
   be called with the current template variables as keyword parameters. The return value of the
   function is expected to be a dictionary which will be used to update the template variables.
