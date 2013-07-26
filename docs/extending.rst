
Extending the basic functionality of a CLLD app
-----------------------------------------------

Static assets
~~~~~~~~~~~~~

CLLD Apps may provide custom css and js code. If this code is placed in the default
locations package/static/project.[css|js], it will automatically be packaged for
production. Note that in this case the code should not contain any URLs relative to
the file, because these may break in production.
