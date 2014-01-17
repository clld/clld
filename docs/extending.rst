
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

1. Define a customized datatable class inheriting from either ``clld.web.datatables.base.DataTable`` or one
of its subclasses in ``clld.web.datatables``.

2. Register this datatable class for the route of the page you want to display it on.
