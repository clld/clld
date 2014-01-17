
Installation
------------

#TODO: recommend forking?

For the time being, the ``clld`` package can only be installed from source. To do so,
you may run the following commands in an activated `virtualenv <http://www.virtualenv.org/en/latest/>`_::

    git clone git@github.com:clld/clld.git
    cd clld
    python setup.py develop

Alternatively, you may want to fork ``clld`` first and then work with your fork.


Bootstrapping a CLLD app
------------------------

A CLLD app is a python package implementing a
`pyramid <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/introduction.html>`_
web application.


The package
~~~~~~~~~~~

The ``clld`` package provides a pyramid application scaffold to create the initial package directory
layout for a CLLD app::

    pcreate -t clld_app myapp

.. notes::

    The ``pcreate`` command has been installed with pyramid as a dependency of ``clld``.

Now create a `configuration file <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/environment.html>`_,
e.g. ``myapp/development.ini`` providing a setting ``sqlalchemy.url`` in the ``[app:main]`` section.
The `SQLAlchemy engine URL <http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html>`_ given in this
setting must point to an existing (although empty) database if the ``postgresql`` dialect is chosen.


The data
~~~~~~~~

Now you can edit ``clld/scripts/initializedb.py`` to fill the database with your data and run::

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
``clld.files`` must point to a directory on the local filesystem. This setting is evaluated
when a file's "create" method is called, or its URL is calculated.

Note that there's an additional category of static files - downloads - which are treated
differently because they are not considered primary but derived data which can be
recreated anytime. To separate these concerns physically, downloads are typically stored
in a different directory than primary data files.


The app
~~~~~~~

You are now ready to run::

    pserve --reload development.ini

and navigate with your browser to http://0.0.0.0:6543 to visit your application.


Examples
--------

A good way explore how to customize a CLLD app is by looking at the code of existing apps.
These apps are listed at `<http://clld.org/datasets>`_ and each app links to its source code
repository on `GitHub <https://github.com/clld>`_ (in the site footer).
