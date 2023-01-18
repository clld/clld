
Getting started
---------------

Requirements
~~~~~~~~~~~~

``clld`` works with python >=3.7. It has been installed and run successfully on
Ubuntu (20.04, 22.04), Mac OSX/scripts and Windows.
While it might be possible to use sqlite as database backend, all production installations
of ``clld`` and most development is done with postgresql (>=9.x).
To retrieve the ``clld`` software from GitHub, ``git`` must be installed on the system.

.. _install:

Installation
~~~~~~~~~~~~

To install the python package from pypi run

.. code-block:: bash

    $ pip install clld[bootstrap]

Note that the above command also installs the ``bootstrap`` extra requirements. These are needed to
create an app skeleton and initialize a database for the app. Thus, when deploying an app to a
production server, copying over a database, you can do without ``bootstrap`` and cut down on
software on the server.


Bootstrapping a ``clld`` app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``clld`` app is a python package implementing a
`pyramid <https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/introduction.html>`_
web application.

Installing the ``clld`` package will also install a command ``clld``,
which offers functionality to kickstart a ``clld`` app project. Note that
this functionality requires the ``cookiecutter`` package to be installed (which will already
be the case if you installed ``clld`` with the ``bootstrap`` extra).

.. code-block:: bash

    $ pip install cookiecutter
    $ clld create myapp

This will create a ``myapp`` project directory, containing a python package ``myapp`` with the following layout::

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
    │   │   ├── initializedb.py      # database initialization code
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


.. note::

    If you are creating a ``clld`` app to serve data from a CLDF dataset, don't forget to specify
    the CLDF module name when prompted. This will provide you with a stub implementation of data
    import code in ``myapp/scripts/initializedb.py`` which is tailored to CLDF data.

    For example if you wanted your ``clld`` app to serve a CLDF StructureDataset such as
    `John Peterson's data <https://doi.org/10.5281/zenodo.3603755>`_ for his paper
    "Towards a linguistic prehistory of eastern-central South Asia", you'd run

    .. code-block:: shell

        $ clld create myapp domain=example.org cldf_module=StructureDataset

    and download the data to be loaded running

    .. code-block:: shell

        $ curl -o petersonsouthasia-v1.1.zip "https://zenodo.org/record/3603755/files/cldf-datasets/petersonsouthasia-v1.1.zip?download=1"
        $ unzip petersonsouthasia-v1.1.zip


Running

.. code-block:: bash

    $ cd myapp
    $ pip install -e .[dev]

will install your app as Python package in development mode, i.e. will create a link to
your app's code in the ``site-packages`` directory. (We also install the ``dev`` extra in order
to have the `waitress <https://docs.pylonsproject.org/projects/waitress/en/stable/index.html>`_
app server available for testing.)

Now edit the `configuration file <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/environment.html>`_,
``myapp/development.ini`` providing a setting ``sqlalchemy.url`` in the ``[app:main]`` section.
The `SQLAlchemy engine URL <https://docs.sqlalchemy.org/en/14/core/engines.html>`_ given in this
setting must point to an existing (but empty) database if the ``postgresql`` dialect is chosen.
If you are happy with using an SQLite database, you can leave the configuration as is.

Running

.. code-block:: bash

    $ clld initdb development.ini

will then create the database for your app. Whenever you edit the database initialization
script, you have to re-run the above command.

.. note::

    If your app serves data from a CLDF dataset - and loads this data from the
    `pycldf.Dataset <https://pycldf.readthedocs.io/en/latest/dataset.html>`_
    instance passed into ``initializedb.main`` as ``args.cldf`` - you must run
    ``clld initdb development.ini --cldf PATH/TO/CLDF/METADATA.json``.

    So if you downloaded and unzipped
    `petersonsouthasia-v1.1.zip <https://zenodo.org/record/3603755/files/cldf-datasets/petersonsouthasia-v1.1.zip?download=1>`_
    you should run

    .. code-block:: shell

        $ clld initdb development.ini --cldf ../cldf-datasets-petersonsouthasia-e029fbf/cldf/StructureDataset-metadata.json


You are now ready to run

.. code-block:: bash

    $ pserve --reload development.ini

and navigate with your browser to http://127.0.0.1:6543 to visit your application.

The next step is populating the database (unless you are happy with the defaults provided for
CLDF datasets).


Testing
~~~~~~~

The ``clld`` app skeleton comes with a stub test suite consisting in ``myapp/tests/``. To run these
tests, install the requirements

.. code-block:: bash

    $ pip install -e .[test]

and run the tests with

.. code-block:: bash

    $ pytest

.. note::

    The `selenium tests <https://selenium-python.readthedocs.io/installation.html>`_ are run on
    Firefox, so you'd need to have Firefox installed as well as the corresponding
    `driver <https://selenium-python.readthedocs.io/installation.html#drivers>`_


Populating the database
~~~~~~~~~~~~~~~~~~~~~~~

The ``clld`` framework does not provide any GUI or web interface for populating the database.
Instead, this is assumed to be done with code in
``myapp/scripts/initializedb.py`` which is run via

.. code-block:: bash

    $ clld initdb development.ini

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

.. autoclass:: clld.cliutil.Data
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

.. note::

    If your app serves the data from a published CLDF dataset (as is recommended), you can specify
    metadata of the published dataset in ``myapp/appconf.ini``. This metadata will be used on the
    download page to guide users to the data. The relevant settings are in the ``[clld]`` section:

    .. code-block:: ini

        # Version-independent concept DOI on Zenodo (see https://help.zenodo.org/#versioning)
        zenodo_concept_doi =
        # DOI for the exact version of the dataset on Zenodo
        zenodo_version_doi =
        # Version tag
        zenodo_version_tag =
        # GitHub repository in which the dataset is curated, specified as "org/repos"
        dataset_github_repos =


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

The ``clld`` apps maintained by the MPI EVA in Leipzig are deployed and managed using the
`clldappconfig package <https://github.com/dlce-eva/clldappconfig>`_
Reading through the code of the
`deploy task <https://github.com/dlce-eva/clldappconfig/blob/68bcef6c90f7973d92d8e6f9248523f751425aa7/src/clldappconfig/tasks/deployment.py#L202>`_
should give you a good idea of the things to keep in mind when deploying ``clld`` apps productively.


Examples
~~~~~~~~

A good way explore how to customize a ``clld`` app is by looking at the code of existing apps.
These apps are listed at `<https://clld.org/datasets.html>`_ and each app links to its source code
repository on `GitHub <https://github.com/clld>`_ (in the site footer).
