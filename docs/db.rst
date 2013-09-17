
Database
--------

The clld data model includes the following entities commonly found in linguistic databases and publications:


.. automodule:: clld.db.models.common
    :members:


Extensibility
~~~~~~~~~~~~~

The core clld data model can be extended by clld apps in two ways:
- Additional models deriving from clld.db.meta.Base can be defined.
- Customizations of core models can be defined using joined table inheritance.


Versioning
~~~~~~~~~~

TODO


Migrations
~~~~~~~~~~

Migrations provide a mechanism to update the database model (or the data) in a controlled
and repeatable way. CLLD apps use alembic to implement migrations.

