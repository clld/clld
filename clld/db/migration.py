"""Functionality for alembic scripts.

This module provides

- basic crud functionality within alembic migration scripts,
- advanced helpers for special tasks, like merging sources.

.. note::

    Using the functionality provided in this module is not possible for Alembic scripts
    supposed to be run in
    `offline mode <http://alembic.readthedocs.org/en/latest/tutorial.html\
    #generating-sql-scripts-a-k-a-offline-mode>`_.
"""

from sqlalchemy.sql import select as base_select, func
from clld.db.models import common


def _with_where_clause(table, stmt, **where):
    for key, value in where.items():
        stmt = stmt.where(getattr(table.c, key) == value)
    return stmt


class Connection(object):

    """A wrapper around an SQLAlchemy connection.

    This wrapper provides the convenience of allowing typical CRUD operations to be
    called passing model classes.

    Additionally, it implements more complicated clld domain specific database
    operations.

    A ``Connection`` will typically be instantiated in an Alembic migration script as
    follows:

    .. code-block:: python

        from alembic import op
        conn = Connection(op.get_bind())
    """

    def __init__(self, conn):
        """Initialize.

        :param conn:
            SQLAlchemy connection object, i.e. anything with a ``execute`` method; so in
            particular a session qualifies as well as an engine, i.e. what ``get_bind()``
            returns.
        """
        self._conn = conn

    def execute(self, *args, **kw):
        """Provide access to the underlying connection's ``execute`` method."""
        return self._conn.execute(*args, **kw)

    #
    # CRUD operations:
    #
    def select(self, model, **where):
        """Run a select statement and return a ResultProxy."""
        table = model.__table__
        return self.execute(_with_where_clause(table, base_select([table]), **where))

    def all(self, model, **where):
        """return all results of a select statement."""
        return self.select(model, **where).fetchall()

    def first(self, model, **where):
        """return first result of a select statement or ``None``."""
        return self.select(model, **where).fetchone()

    def get(self, model, pk):
        """return row specified by primary key."""
        return self.first(model, pk=pk)

    def pk(self, model, id_, attr='id'):
        """Get the primary key of an object specified by a unique property.

        :param model: model class.
        :param id_: Value to be used when filtering.
        :param attr: Column to be used for filtering.
        :return: primary key of (first) matching row.
        """
        res = self.first(model, **{attr: id_})
        if res:
            return res.pk

    def insert(self, model, **values):
        """Run an insert statement.

        :return: primary key of the inserted row.
        """
        for k, v in [
            ('version', 1),
            ('created', func.now()),
            ('updated', func.now()),
            ('active', True)
        ]:
            if hasattr(model.__table__.c, k):
                values.setdefault(k, v)

        res = self.execute(model.__table__.insert().values(**values))
        return res.inserted_primary_key[0]

    def update(self, model, values, **where):
        """Run an update statement."""
        if not isinstance(values, dict):
            values = dict(values)
        if hasattr(model.__table__.c, 'updated'):
            values.setdefault('updated', func.now())
        table = model.__table__
        self.execute(_with_where_clause(table, table.update(), **where).values(**values))

    def delete(self, model, **where):
        """Run a delete statement."""
        self.execute(
            _with_where_clause(model.__table__, model.__table__.delete(), **where))

    #
    # domain specific operations:
    #
    def set_glottocode(self, lid, gc, gcid=None):
        """assign a unique glottocode to a language.

        i.e. alternative glottocodes will be deleted.

        :param lid: ``id`` of the language.
        :param gc: Glottocode to be assigned.
        :param gcid:
            ``id`` of the ``Identifier`` instance if one has to be created;
            defaults to ``gc``.
        """
        lpk = self.pk(common.Language, lid)
        gctype = common.IdentifierType.glottolog.value

        done = False
        lis = self.all(common.LanguageIdentifier, language_pk=lpk)
        for li in lis:
            i = self.get(common.Identifier, li.identifier_pk)
            if i.type == gctype:
                if i.name == gc:
                    done = True
                else:
                    self.delete(common.LanguageIdentifier, pk=li.pk)

        if not done:
            # create a new relation
            i = self.first(common.Identifier, name=gc, type=gctype)
            if i:
                ipk = i.pk
            else:
                ipk = self.insert(common.Identifier, id=gcid or gc, name=gc, type=gctype)
            return self.insert(
                common.LanguageIdentifier, language_pk=lpk, identifier_pk=ipk)

    def replace(self, model, from_id, to_id):  # pragma: no cover
        self.insert(
            common.Config, key=common.Config.replacement_key(model, from_id), value=to_id)


def merge_sources(conn, from_id, to_id, *fields):  # pragma: no cover
    if not isinstance(conn, Connection):
        conn = Connection(conn)
    # resolve id to pk
    fpk = conn.pk(common.Source, from_id)
    tpk = conn.pk(common.Source, to_id)

    if fields:
        conn.execute("""\
UPDATE source
SET %s
FROM (SELECT %s FROM source WHERE pk = %s) AS old
WHERE pk = %s""" % (', '.join('{0}=old.{0}'.format(f) for f in fields),
                    ', '.join(fields),
                    fpk,
                    tpk))

    # update relationships
    for row in conn.all(common.LanguageSource, source_pk=fpk):
        lpk = row['language_pk']
        if conn.first(common.LanguageSource, language_pk=lpk, source_pk=tpk):
            conn.delete(common.LanguageSource, source_pk=fpk)
        else:
            conn.update(common.LanguageSource, dict(source_pk=tpk), source_pk=fpk)

    for model in [
        common.SentenceReference, common.ContributionReference, common.ValueSetReference
    ]:
        conn.update(model, dict(source_pk=tpk), source_pk=fpk)

    # add replacement record
    conn.replace(common.Source, from_id, to_id)

    # remove source
    conn.delete(common.Source, id=from_id)
