"""We provide some infrastructure to build extensible database models."""
import sqlite3
import json

from six import string_types, PY2

from sqlalchemy import (
    Column, Integer, Float, String, Boolean, DateTime, func, event)
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.pool import Pool
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker, deferred, undefer
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.query import Query
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.postgresql import TSVECTOR

from zope.sqlalchemy import ZopeTransactionExtension
from clldutils.misc import NO_DEFAULT, UnicodeMixin
from clldutils import jsonlib

from clld.db.versioned import versioned_session


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """Event listener to handle disconnects.

    Implements
    `pessimistic disconnect handling <http://docs.sqlalchemy.org/en/rel_0_9/core/\
    pooling.html#disconnect-handling-pessimistic>`_.

    .. note::

        Our implementation is mildly dialect specific, but works for sqlite and
        PostgreSQL. For oracle, the 'ping' query should read *SELECT 1 FROM DUAL* or
        similar.
    """
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
        if not isinstance(dbapi_connection, sqlite3.Connection):  # pragma: no cover
            cursor.execute("SET default_text_search_config TO 'english'")
    except:  # pragma: no cover
        # dispose the whole pool instead of invalidating one at a time
        connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise DisconnectionError()
    cursor.close()


class ActiveOnlyQuery(Query):  # pragma: no cover

    """A pre-filtering query.

    Implements a
    `pre-filtering query <http://www.sqlalchemy.org/trac/wiki/UsageRecipes/\
    PreFilteredQuery>`_ that filters on the :py:attr:`clld.db.meta._Base.active` flag.
    """

    def get(self, ident):
        # override get() so that the flag is always checked in the
        # DB as opposed to pulling from the identity map.
        return Query.get(self.populate_existing(), ident)

    def __iter__(self):
        return Query.__iter__(self.private())

    def from_self(self, *ent):
        # override from_self() to automatically apply
        # the criterion too.   this works with count() and
        # others.
        return Query.from_self(self.private(), *ent)

    def private(self):
        mzero = self._mapper_zero()
        if mzero is not None:
            crit = mzero.class_.active == True
            return self.enable_assertions(False).filter(crit)
        else:
            return self


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
ActiveOnlyDBSession = scoped_session(sessionmaker(
    extension=ZopeTransactionExtension(), query_cls=ActiveOnlyQuery))
VersionedDBSession = scoped_session(versioned_session(
    sessionmaker(autoflush=False, extension=ZopeTransactionExtension())))


class JSONEncodedDict(TypeDecorator):

    """Represents an immutable structure as a json-encoded string.

    Loads/serializes an empty dict for any empty value.
    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if not value:
            value = {}
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if not value:
            return {}
        return json.loads(value)


class CsvMixin(object):

    """Mixin providing methods to control (de-)serialization of an object as csv row."""

    #: base name of the csv file
    __csv_name__ = None

    @classmethod
    def csv_head(cls):
        """return List of column names."""
        exclude = {'active', 'version', 'created', 'updated', 'polymorphic_type'}
        cols = sorted(
            col.key for om in inspect(cls).iterate_to_root()
            for col in om.local_table.c
            if (col.key not in exclude
                and col.type.__class__ not in [TSVECTOR]
                and not exclude.add(col.key)))
        return cols

    def value_to_csv(self, attr, ctx=None, req=None):
        """Convert one value to a representation suitable for csv writer.

        :param attr: Name of the attribute from which to convert the value.
        :return: Object suitable for serialization with csv writer.
        """
        rel = None
        if attr.endswith('__ids') or attr.endswith('__id'):
            attr = attr.split('__')
            rel = attr[-1]
            attr = '__'.join(attr[:-1])
        prop = getattr(self, attr, '')
        if attr == 'jsondata':
            prop = json.dumps(prop)
            if PY2:
                prop = prop.decode('utf8')
        if rel == 'id' and hasattr(prop, 'id'):
            return prop.id
        elif rel == 'ids':
            return ','.join('%s' % o.id for o in prop)
        return prop

    def to_csv(self, ctx=None, req=None, cols=None):
        """return list of values to be passed to csv.writer.writerow."""
        return [self.value_to_csv(attr, ctx, req) for attr in cols or self.csv_head()]

    @classmethod
    def value_from_csv(cls, attr, value):
        if not value:
            return None
        col = getattr(cls, attr)
        if hasattr(col, 'property') and hasattr(col.property, 'columns'):
            if isinstance(col.property.columns[0].type, Integer):
                return int(value)
            if isinstance(col.property.columns[0].type, Float):
                if isinstance(value, string_types):
                    value = value.replace(',', '.')
                return float(value)
        return value

    @classmethod
    def from_csv(cls, row, data=None, cols=None):
        obj = cls()
        cols = cols or obj.csv_head()
        for i, k in enumerate(cols):
            if not (k.endswith('__id') or k.endswith('__ids')) and hasattr(obj, k):
                setattr(obj, k, cls.value_from_csv(k, row[i]) or None)
        return obj

    @classmethod
    def csv_query(cls, session):
        query = session.query(cls).filter_by(active=True)
        return query.order_by(getattr(cls, 'id', getattr(cls, 'pk', None)))


class Base(UnicodeMixin, CsvMixin, declarative_base()):

    """The declarative base for all our models."""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        """We derive the table name from the model class name.

        This should be safe,
        because we don't want to have model classes with the same name either.
        Care has to be taken, though, to prevent collisions with the names of tables
        which are automatically created (history tables for example).
        """
        return cls.__name__.lower()

    #: All our models have an integer primary key which has nothing to do with
    #: the kind of data stored in a table. 'Natural' candidates for primary keys
    #: should be marked with unique constraints instead. This adds flexibility
    #: when it comes to database changes.
    pk = Column(Integer, primary_key=True, doc='primary key')

    #: To allow for timestamp-based versioning - as opposed or in addition to the version
    #: number approach implemented in :py:class:`clld.db.meta.Versioned` - we store
    #: a timestamp for creation or an object.
    @declared_attr
    def created(cls):
        return deferred(Column(DateTime(timezone=True), default=func.now()))

    #: Timestamp for latest update of an object.
    @declared_attr
    def updated(cls):
        return deferred(Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))

    #: The active flag is meant as an easy way to mark records as obsolete or inactive,
    #: without actually deleting them. A custom Query class could then be used which
    #: filters out inactive records.
    @declared_attr
    def active(cls):
        return deferred(Column(Boolean, default=True))

    #: To allow storage of arbitrary key,value pairs with typed values, each model
    #: provides a column to store JSON encoded dicts.
    jsondata = Column(JSONEncodedDict)

    def __init__(self, jsondata=None, **kwargs):
        kwargs['jsondata'] = jsondata or {}
        super(Base, self).__init__(**kwargs)

    def update_jsondata(self, **kw):
        """Convenience function.

        Since we use the simple
        `JSON encoded dict recipe <http://docs.sqlalchemy.org/en/rel_0_9/core/types.html\
        #marshal-json-strings>`_
        without mutation tracking, we provide a convenience method to update
        """
        d = self.jsondata.copy()
        d.update(kw)
        self.jsondata = d

    @property
    def jsondatadict(self):
        """Deprecated convenience function.

        Use jsondata directly instead, which is guaranteed to be a dictionary.
        """
        return self.jsondata or {}

    @property
    def replacement_id(self):
        """Used to allow automatically redirecting to a 'better' version of a resource."""
        if not self.active:
            return self.jsondata.get('__replacement_id__')

    @classmethod
    def get(cls, value, key=None, default=NO_DEFAULT, session=None):
        """Convenience method to query a model where exactly one result is expected.

        e.g. to retrieve an instance by primary key or id.

        :param value: The value used in the filter expression of the query.
        :param str key: The key or attribute name to be used in the filter expression. If\
        None is passed, defaults to *pk* if value is ``int`` otherwise to *id*.
        """
        session = session or DBSession
        if key is None:
            key = 'pk' if isinstance(value, int) else 'id'
        try:
            return session.query(cls)\
                .options(undefer('updated')).filter_by(**{key: value}).one()
        except (NoResultFound, MultipleResultsFound):
            if default is NO_DEFAULT:
                raise
            return default

    @classmethod
    def first(cls):
        """More convenience."""
        return DBSession.query(cls).order_by(cls.pk).first()

    def history(self):
        """return result proxy to iterate over previous versions of a record."""
        model = self.__class__
        if not hasattr(model, '__history_mapper__'):
            return []  # pragma: no cover

        history_class = model.__history_mapper__.class_
        return DBSession.query(history_class).filter(history_class.pk == self.pk)\
            .order_by(history_class.version.desc())

    def __json__(self, req):
        """Custom JSON serialization of an object.

        :param req: pyramid Request object.
        :return: ``dict`` suitable for serialization as JSON.
        """
        exclude = {'active', 'version', 'created', 'updated', 'polymorphic_type'}
        cols = [
            col.key for om in inspect(self).mapper.iterate_to_root()
            for col in om.local_table.c
            if col.key not in exclude and not exclude.add(col.key)]
        return {col: jsonlib.format(getattr(self, col)) for col in cols}

    def __unicode__(self):
        """A human readable label for the object."""
        r = getattr(self, 'name', None)
        if not r:
            r = getattr(self, 'id', None)
        if not r:
            r = '%s%s' % (self.__class__.__name__, self.pk)
        return r

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__, getattr(self, 'id', self.pk))


class PolymorphicBaseMixin(object):

    """Mixin providing the wiring for joined table inheritance.

    We use joined table inheritance to allow projects to augment base ``clld``
    models with project specific attributes. This mixin class prepares
    models to serve as base classes for inheritance.
    """

    polymorphic_type = Column(String(20))

    @declared_attr
    def __mapper_args__(cls):
        return {
            'polymorphic_on': cls.polymorphic_type,
            'polymorphic_identity': 'base',
            'with_polymorphic': '*',
        }


def is_base(cls):
    """Determine whether a class is a base class or an inheriting one.

    :param cls: Model class.
    :return: ``bool`` signaling whether ``cls`` is a base class or derived, i.e.\
    customized.
    """
    # replace with inspection?
    # see http://docs.sqlalchemy.org/en/rel_0_9/orm/mapper_config.html
    # ?highlight=polymorphic_identity#sqlalchemy.orm.mapper.Mapper.polymorphic_identity
    return PolymorphicBaseMixin in cls.__bases__


class CustomModelMixin(object):

    """Mixin for customized classes in our joined table inheritance scheme.

    .. note::

        With this scheme there can be only one specialized mapper class per inheritable
        base class.
    """

    @declared_attr
    def __mapper_args__(cls):
        return {'polymorphic_identity': 'custom'}  # pragma: no cover
