
Database
--------

The clld data model includes the following entities commonly found in linguistic databases and publications:


.. automodule:: clld.db.models.common
    :members:
    :exclude-members: relationship, desc


Extensibility
~~~~~~~~~~~~~

The core clld data model can be extended by clld apps in two ways:

- Additional models (thus additional database tables) deriving from :py:class:`clld.db.meta.Base` can be defined.
- Customizations of core models can be defined using joined table inheritance::

.. code-block:: python
    :emphasize-lines: 7,8,12

    from sqlalchemy import Column, Integer, ForeignKey
    from zope.interface import implementer
    from clld.interfaces import IContribution
    from clld.db.meta import CustomModelMixin
    from clld.db.models.common import Contribution

    @implementer(IContribution)
    class Chapter(Contribution, CustomModelMixin):
        """Contributions in WALS are chapters chapters. These comprise a set of features with
        corresponding values and a descriptive text.
        """
        pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
        # add more Columns and relationships here


Versioning
~~~~~~~~~~

Versioned model objects are supported via the :py:class:`clld.db.versioned.Versioned` mixin,
implemented following the corresponding
`SQLAlchemy ORM Example <http://docs.sqlalchemy.org/en/rel_0_9/orm/examples.html#module-examples.versioned_history>`_.


Migrations
~~~~~~~~~~

Migrations provide a mechanism to update the database model (or the data) in a controlled
and repeatable way. CLLD apps use alembic to implement migrations.
