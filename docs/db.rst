
Database
--------

The clld data model includes the following entities commonly found in linguistic databases and publications:

.. automodule:: clld.db.models.common
    :members:
    :exclude-members: relationship, desc

Custom models may be defined for CLLD apps making use of the base classes and mixins

.. automodule:: clld.db.meta
    :members:
    :exclude-members: relationship, desc


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
and repeatable way. CLLD apps use alembic to implement migrations.
