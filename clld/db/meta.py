"""
We provide some infrastructure to build extensible database models.
"""
from copy import copy
from datetime import datetime
try:
    import simplejson as json
except ImportError:
    import json

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    Boolean,
    desc,
    exc,
    event,
)
from sqlalchemy.pool import Pool
from sqlalchemy.ext.declarative import (
    declarative_base,
    declared_attr,
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    object_mapper,
    class_mapper,
)
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from zope.sqlalchemy import ZopeTransactionExtension

from clld.db.versioned import versioned_session
from clld.util import NO_DEFAULT, UnicodeMixin


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:  # pragma: no cover
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
VersionedDBSession = scoped_session(versioned_session(
    sessionmaker(autoflush=False, extension=ZopeTransactionExtension())))


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)
    """
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class Base(UnicodeMixin):
    """All our models have an integer primary key which has nothing to do with
    the kind of data stored in a table. 'Natural' candidates for primary keys
    should be marked with unique constraints instead. This adds flexibility
    when it comes to database changes.
    """
    @declared_attr
    def __tablename__(cls):
        """We derive the table name from the model class name. This should be safe,
        because we don't want to have model classes with the same name either.
        Care has to be taken, though, to prevent collisions with the names of tables
        which are automatically created (history tables for example).
        """
        return cls.__name__.lower()

    pk = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # The active flag is meant as an easy way to mark records as obsolete or inactive,
    # without actually deleting them. A custom Query class could then be used which
    # filters out inactive records.
    active = Column(Boolean, default=True)

    # To allow storage of key,value pairs with typed values:
    jsondata = Column(JSONEncodedDict)

    def update_jsondata(self, **kw):
        #
        # TODO: remove hack after successful data import of glottolog 2
        #
        import json
        if isinstance(self.jsondata, basestring):
            self.jsondata = json.loads(self.jsondata)

        d = copy(self.jsondata) or {}
        d.update(**kw)
        self.jsondata = d

    @classmethod
    def mapper_name(cls):
        return class_mapper(cls).class_.__name__

    @property
    def jsondatadict(self):
        return self.jsondata or {}

    @classmethod
    def get(cls, value, key=None, default=NO_DEFAULT):
        """A convenience method.
        """
        if key is None:
            key = 'pk' if isinstance(value, int) else 'id'
        try:
            return DBSession.query(cls).filter_by(**{key: value}).one()
        except (NoResultFound, MultipleResultsFound):
            if default is NO_DEFAULT:
                raise
            return default

    @classmethod
    def first(cls):
        """More convenience.
        """
        return DBSession.query(cls).order_by(cls.pk).first()

    def history(self):
        """
        :return: Result proxy to iterate over previous versions of a record.
        """
        model = object_mapper(self).class_
        if not hasattr(model, '__history_mapper__'):
            return []

        history_class = model.__history_mapper__.class_
        return DBSession.query(history_class).filter(history_class.pk == self.pk)\
            .order_by(desc(history_class.version))

    def __json__(self, req):
        cols = []
        for om in object_mapper(self).iterate_to_root():
            cols.extend(col.key for col in om.local_table.c)
        return dict(
            (col, getattr(self, col))
            for col in set(cols) if col not in ['created', 'updated'])

    def __unicode__(self):
        """
        :return: a human readable label for the object
        """
        r = getattr(self, 'name', None)
        if not r:
            r = getattr(self, 'id', None)
        if not r:
            r = repr(self)[1:].split('object')[0] + ('%s' % self.pk)
        return r

    def __repr__(self):
        return '%s-%s' % (
            object_mapper(self).class_.__name__, getattr(self, 'id', self.pk))


Base = declarative_base(cls=Base)


class PolymorphicBaseMixin(object):
    """We use joined table inheritance to allow projects to augment base clld
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


class CustomModelMixin(object):
    """Mixin for inheriting classes in our joined table inheritance scheme.

    .. note::

        With this scheme there can be only one specialized mapper class per inheritable
        base class.
    """
    @declared_attr
    def __mapper_args__(cls):
        return {'polymorphic_identity': 'custom'}  # pragma: no cover
