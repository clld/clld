
Extending the basic functionality of a CLLD app
-----------------------------------------------

Extending or customizing the default behaviour of a CLLD app is basically what pyramid
calls `configuration <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/configuration.html>`_.
So, since the ``clld_app`` scaffold is somewhat tuned towards imperative configuration,
this means calling methods on the config object returned by the call to
:py:func:`clld.web.app.get_configurator` in the apps ``main`` function.
Since the config object is an instance of the pyramid
`Configurator <http://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator>`_
this includes all the standard ways to configure pyramid apps, in particular adding
routes and views to provide additional pages and funtionality with an app.


Static assets
~~~~~~~~~~~~~

CLLD Apps may provide custom css and js code. If this code is placed in the default
locations ``myapp/static/project.[css|js]``, it will automatically be packaged for
production. Note that in this case the code should not contain any URLs relative to
the file, because these may break in production.

Other static content can still be placed in the ``myapp/static`` directory but must be
explicitely included on pages making use of it, e.g. with template code like:

.. code-block:: html

    <link href="${request.static_url('myapp:static/css/introjs.min.css')}" rel="stylesheet">
    <script src="${request.static_url('myapp:static/js/intro.min.js')}"></script>


Menu Items
~~~~~~~~~~

Registering non-default menu items can only be done wholesale, i.e. replacing the whole
main menu by calling the ``register_menu`` method of the config object.

.. py:function:: register_menu(*items) #*

    :param items: (name, factory) pairs, where factory is a callable that accepts the two parameters (ctx, req) and returns a pair (url, label) to use for the menu link and name is used to compare with the ``active_menu`` attribute of templates.


Datatables
~~~~~~~~~~

A main building block of CLLD apps are dynamic data tables. Although there are default
implementations which may be good enough in many cases, each data table can be fully
customized as follows.

1. Define a customized datatable class in ``myapp/datables.py`` inheriting from either
:py:class:`clld.web.datatables.base.DataTable` or one
of its subclasses in :py:mod:`clld.web.datatables`.

2. Register this datatable for the page you want to display it on by
adding a line like the following to the function ``myapp.datatables.includeme``::

    config.register_datatable('routename', DataTableClassName)

The ``register_datatable`` method of the config object has the following signature:

.. py:function:: register_datatable(route_name, cls)

    :param str route_name: Name of the route which maps to the view serving the page (see :ref:`sec-resource-routes`).
    :param class cld: Python class inheriting from :py:class:`clld.web.datatables.base.DataTable`.


Customize column definitions
++++++++++++++++++++++++++++

Overwrite :py:meth:`clld.web.datatables.base.DataTable.col_defs`.


Customize query
++++++++++++++++

Overwrite :py:meth:`clld.web.datatables.base.DataTable.base_query`.


Data model
~~~~~~~~~~

The core ``clld`` data model can be extended for CLLD apps by defining additional
`mappings <http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#declare-a-mapping>`_
in ``myapp.models`` in two ways:

- Additional mappings (thus additional database tables) deriving from :py:class:`clld.db.meta.Base`
  can be defined.
- Customizations of core models can be defined using joined table inheritance:

.. code-block:: python
    :emphasize-lines: 7,8,12

    from sqlalchemy import Column, Integer, ForeignKey
    from zope.interface import implementer
    from clld.interfaces import IContribution
    from clld.db.meta import CustomModelMixin
    from clld.db.models.common import Contribution

    @implementer(IContribution)
    class Chapter(Contribution, CustomModelMixin):
        """Contributions in WALS are chapters chapters. These comprise a set of features with
        corresponding values and a descriptive text.
        """
        pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
        # add more Columns and relationships here

