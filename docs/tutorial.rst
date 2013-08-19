
Installation
------------

TODO: recommend forking?

In a virtualenv::

    pip install -e github...


Bootstrapping a CLLD app
------------------------

The package
~~~~~~~~~~~

The clld package provides a pyramid app scaffold to create the initial package directory
layout for a clld app::

    pcreate -t clld_app myapp

Create a configuration file, e.g. development.ini


The data
~~~~~~~~

Edit initializedb.py to fill the database with your data and run::

    python myapp/scripts/initializedb.py development.ini


The app
~~~~~~~

You are now ready to run::

    pserve --reload development.ini

and navigate with your browser to http://0.0.0.0:6543 visit your application.
