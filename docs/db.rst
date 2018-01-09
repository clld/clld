
Database
--------

The ``clld`` database models are declared using SQLAlchemy's
`declarative <http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/index.html>`_
extension. In particular we follow the approach of
`mixins and custom base class <http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/mixins.html>`_,
to provide building blocks with enough shared commonality for custom data models.

.. _db_objects:

Declarative base and mixins
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: clld.db.meta.Base
    :members:
    :exclude-members: first, replacement_id


.. autoclass:: clld.db.meta.CustomModelMixin

.. autoclass:: clld.db.models.common.IdNameDescriptionMixin
    :members:


While the above mixin only adds columns to a model, the following mixins do also add
relations between models, thus have to be used in combination, tied together by naming
conventions.

.. autoclass:: clld.db.models.common.DataMixin
    :members:

.. autoclass:: clld.db.models.common.HasDataMixin
    :members:

.. autoclass:: clld.db.models.common.FilesMixin
    :members:

.. autoclass:: clld.db.models.common.HasFilesMixin
    :members:

Typical usage looks like

.. code-block:: python

    class MyModel_data(Base, Versioned, DataMixin):
        pass

    class MyModel_files(Base, Versioned, FilesMixin):
        pass

    class MyModel(Base, HasDataMixin, HasFilesMixin):
        pass




Core models
~~~~~~~~~~~

The CLLD data model includes the following entities commonly found in linguistic databases
and publications:

.. autoclass:: clld.db.models.common.Dataset
    :members:

.. autoclass:: clld.db.models.common.Language
    :members:

.. autoclass:: clld.db.models.common.Parameter
    :members:

.. autoclass:: clld.db.models.common.ValueSet
    :members:

.. autoclass:: clld.db.models.common.Value
    :members:

.. autoclass:: clld.db.models.common.Contribution
    :members:

.. autoclass:: clld.db.models.common.Contributor
    :members:

.. autoclass:: clld.db.models.common.Source
    :members:

.. autoclass:: clld.db.models.common.Unit
    :members:

.. autoclass:: clld.db.models.common.UnitParameter
    :members:

.. autoclass:: clld.db.models.common.UnitValue
    :members:


Versioning
~~~~~~~~~~

Versioned model objects are supported via the :py:class:`clld.db.versioned.Versioned` mixin,
implemented following the corresponding
`SQLAlchemy ORM Example <http://docs.sqlalchemy.org/en/rel_0_9/orm/examples.html#module-examples.versioned_history>`_.

.. automodule:: clld.db.versioned
    :members:
    :exclude-members: relationship, desc, mapper


Migrations
~~~~~~~~~~

Migrations provide a mechanism to update the database model (or the data) in a controlled
and repeatable way. ``clld`` apps use
`Alembic <http://alembic.readthedocs.org/en/latest/>`_ to implement migrations.

Since a migration may change the database schema, it is generally not possible to fully
use ORM mechanisms in migration scripts. Instead, migration scripts typically construct
SQL to be sent to the database "by hand", or using SQLAlchemy's
`SQL expression language <http://docs.sqlalchemy.org/en/latest/core/tutorial.html>`_.
Now dropping down to these lower levels of database access makes scripts verbose and
error prone. Thus, ``clld`` provides a module with helpers for Alembic migration scripts.

.. automodule:: clld.db.migration
    :members:
    :exclude-members: base_select
