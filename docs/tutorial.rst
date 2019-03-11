
Getting started
---------------

Requirements
~~~~~~~~~~~~

``clld`` works with python 2.7 and >=3.4. It has been installed and run successfully on
Ubuntu (12.04, 14.04, 16.04), Mac OSX (see :ref:`install_mac`) and Windows (see :ref:`install_win`).
While it might be possible to use sqlite as database backend, all production installations
of ``clld`` and most development is done with postgresql (9.1 or 9.3).
To retrieve the ``clld`` software from GitHub, ``git`` must be installed on the system.

.. _install:

Installation
~~~~~~~~~~~~

To install the python package from pypi run

.. code:: bash

    $ pip install clld

To install from a git repository (if you want to hack on ``clld``),
you may run the following commands in an activated `virtualenv <http://www.virtualenv.org/en/latest/>`_:

.. code:: bash

    $ git clone https://github.com/clld/clld.git
    $ cd clld
    $ pip install -r requirements.txt

Alternatively, you may want to fork ``clld`` first and then work with your fork.


Bootstrapping a ``clld`` app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``clld`` app is a python package implementing a
`pyramid <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/introduction.html>`_
web application.

The ``clld`` package provides a pyramid application scaffold to create the initial package directory
layout for a ``clld`` app:

.. code:: bash

    $ pcreate -t clld_app myapp

.. note::

    The ``pcreate`` command has been installed with pyramid as a dependency of ``clld``.

This will create a python package ``myapp`` with the following layout::

    (clld)robert@astroman:~/venvs/clld$ tree myapp/
    myapp/                           # project directory
    ├── development.ini              # deployment settings
    ├── MANIFEST.in
    ├── myapp                        # package directory
    │   ├── adapters.py              # custom adapters
    │   ├── appconf.ini              # custom application settings
    │   ├── assets.py                # registers custom static assets with the clld framework
    │   ├── datatables.py            # custom datatables
    │   ├── __init__.py              # contains the main function
    │   ├── interfaces.py            # custom interface specifications
    │   ├── locale                   # locale directory, may be used for custom translations
    │   │   └── myapp.pot
    │   ├── maps.py                  # custom map objects
    │   ├── models.py                # custom database objects
    │   ├── scripts
    │   │   ├── initializedb.py      # database initialization script
    │   │   └── __init__.py
    │   ├── static                   # custom static assets
    │   │   ├── project.css
    │   │   └── project.js
    │   ├── templates                # custom mako templates
    │   │   ├── dataset              # custom templates for resources of type Dataset
    │   │   │   └── detail_html.mako # the home page of the app
    │   │   └── myapp.mako           # custom site template
    │   ├── tests
    │   │   ├── conftest.py
    │   │   ├── test_functional.py
    │   │   └── test_selenium.py
    │   └── views.py
    ├── README.txt
    ├── setup.cfg
    └── setup.py


Running

.. code:: bash

    $ cd myapp
    $ pip install -e .

will install your app as Python package in development mode, i.e. will create a link to
your app's code in the ``site-packages`` directory.

Now edit the `configuration file <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/environment.html>`_,
``myapp/development.ini`` providing a setting ``sqlalchemy.url`` in the ``[app:main]`` section.
The `SQLAlchemy engine URL <http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html>`_ given in this
setting must point to an existing (but empty) database if the ``postgresql`` dialect is chosen.

Running

.. code:: bash

    $ python myapp/scripts/initializedb.py development.ini

will then create the database for your app. Whenever you edit the database initialization
script, you have to re-run the above command.

.. note::

    If you are using PostgreSQL as rdbms the above command will not automatically drop
    an existing database, so before running it, you have to drop and re-create and empty
    database "by hand".

You are now ready to run

.. code:: bash

    $ pserve --reload development.ini

and navigate with your browser to http://127.0.0.1:6543 to visit your application.

The next step is populating the database.


Populating the database
~~~~~~~~~~~~~~~~~~~~~~~

The ``clld`` framework does not provide any GUI or web interface for populating the database.
Instead, this is assumed to be done with a script.
You can edit ``clld/scripts/initializedb.py`` to fill the database with your data and run

.. code:: bash

    $ python myapp/scripts/initializedb.py development.ini

Adding objects to the database is done by instantiating model objects and
`adding them <http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#adding-new-objects>`_
to ``clld.db.meta.DBSession``. (This session is already initialized when your code in ``initializedb.py`` runs.)
For more information about database objects read the chapter :ref:`db_objects`.

A minimal example (building upon the default ``main`` function in ``initializedb.py`` as created
for the app skeleton) adding just two `Value` objects may look as follows

.. code-block:: python

    def main(args):
        data = Data()

        dataset = common.Dataset(id=myapp.__name__, domain='myapp.clld.org')
        DBSession.add(dataset)

        # All ValueSets must be related to a contribution:
        contrib = common.Contribution(id='contrib', name='the contribution')

        # All ValueSets must be related to a Language:
        lang = common.Language(id='lang', name='A Language', latitude=20, longitude=20)

        param = common.Parameter(id='param', name='Feature 1')

        # ValueSets group Values related to the same Language, Contribution and
        # Parameter
        vs = common.ValueSet(id='vs', language=lang, parameter=param, contribution=contrib)

        # Values store the actual "measurements":
        DBSession.add(common.Value(id='v1', name='value 1', valueset=vs))
        DBSession.add(common.Value(id='v2', name='value 2', valueset=vs))

A more involved example, creating instances of all core model classes, is available in chapter :ref:`initializedb`.

The ``data`` object present in the ``main`` function in ``initializedb.py`` is an instance of

.. autoclass:: clld.scripts.util.Data
    :members:

Thus, you can create objects which you can reference later like

.. code-block:: python

    data.add(common.Language, 'mylangid', id='1', name='French')
    data.add(common.Unit, 'myunitid', id='1', language=data['Language']['mylangid'])

.. note::

    Using ``data.add`` for all objects may not be a good idea for big datasets, because keeping
    references to all objects prevents garbage collection and will blow up the memory used
    for the import process. Some experimentation may be required if you hit this problem.
    As a general rule: only use ``data.add`` for objects that you actually need to lookup
    lateron.

.. note::

    All model classes derived from :py:class:`clld.db.meta.Base` have an integer primary key
    ``pk``. This primary key is defined in such a way (at least for
    `PostgreSQL <http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html#sequences-serial>`_
    and SQLite) that you do not have to specify it when instantiating an object (although you may
    do so).


The dataset
+++++++++++

Each ``clld`` app is assumed to serve a dataset, so you must add an instance of
:py:class:`clld.db.models.common.Dataset`
to your database.
This dataset is assumed to have a publisher
and a license. Information about the publisher and the license should be part of the data,
as well as other metadata about the dataset.


A note on files
+++++++++++++++

A ``clld`` app may have static data files associated with its resources (e.g. soundfiles).
The ``clld`` framework is designed to store these files in the filesystem and just keep
references to them in the database. While this does require a more complex import
and export process, it helps keeping the database small, and allows serving the static
files directly from a webserver instead of having to go through the web application
(which is still possible, though).

To specify where in the filesystem these static files are stored, a configuration setting
``clld.files`` must point to a directory on the local filesystem. This setting is evaluated
when a file's "create" method is called, or its URL is calculated.

Note that there's an additional category of static files - downloads - which are treated
differently because they are not considered primary but derived data which can be
recreated at any time. To separate these concerns physically, downloads are typically stored
in a different directory than primary data files.


Deployment
~~~~~~~~~~

TODO:
clld.environment == 'production',
webassets need to be built.
gunicorn + nginx


Examples
~~~~~~~~

A good way explore how to customize a ``clld`` app is by looking at the code of existing apps.
These apps are listed at `<http://clld.org/datasets.html>`_ and each app links to its source code
repository on `GitHub <https://github.com/clld>`_ (in the site footer).
