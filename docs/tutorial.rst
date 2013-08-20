
Installation
------------

TODO: recommend forking?

In a virtualenv::

    git clone git@github.com:clld/clld.git
    cd clld
    python setup.py develop

You may also want to fork clld first and then work with your fork.


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


A note on files
+++++++++++++++

A clld app may have static data files associated with its resources (e.g. soundfiles).
The clld framework is designed to store these files in the filesystem and just keep
references to them in the database. While this does require a more complex import
and export process, it helps keeping the database small, and allows serving the static
files directly from a webserver instead of having to go through the web application
(which is still possible, though).

To specify where in the filesystem these static files are stored, a configuration setting
"clld.files" must point to a directory on the local filesystem. This setting is evaluated
when a file's "create" method is called, or its URL is calculated.

Note that there's an additional category of static files - downloads - which are treated
differently because they are not considered primary but derived data which can be
recreated anytime. To separate these concerns physically, downloads are typically stored
in a different directory than primary data files.


The app
~~~~~~~

You are now ready to run::

    pserve --reload development.ini

and navigate with your browser to http://0.0.0.0:6543 visit your application.


Examples
--------

Examples of clld apps on the web include:

- `Glottolog <http://glottolog.org>`_ running on the clld app package `glottolog3 <https://github.com/clld/glottolog3>`_

In preparation:

- `APiCS Online <http://apics-online.info>`_ running on the clld app package `apics <https://github.com/clld/apics>`_
- `WALS Online <http://wals.info>`_ running on the clld app package `wals3 <https://github.com/clld/wals3>`_
