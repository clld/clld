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
)
from sqlalchemy.ext.declarative import (
    declarative_base,
    declared_attr,
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.types import TypeDecorator, VARCHAR

from zope.sqlalchemy import ZopeTransactionExtension

from clld.db.versioned import versioned_session


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


class Base(object):
    """All our models have an integer primary key which has nothing to do with
    the kind of data stored in a table. 'Natural' candidates for primary keys
    should be marked with unique constraints instead. This adds flexibility
    when it comes to database changes.
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    pk = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)
    jsondata = Column(JSONEncodedDict)


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
        return {'polymorphic_identity': 'custom'}
