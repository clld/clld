
Extending the basic functionality of a CLLD app
-----------------------------------------------

Static assets
~~~~~~~~~~~~~

CLLD Apps may provide custom css and js code. If this code is placed in the default
locations package/static/project.[css|js], it will automatically be packaged for
production. Note that in this case the code should not contain any URLs relative to
the file, because these may break in production.


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
