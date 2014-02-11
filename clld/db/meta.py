"""
We provide some infrastructure to build extensible database models.
"""
from copy import copy
from datetime import datetime
try:
    import simplejson as json
except ImportError:
    import json

from pytz import UTC
import sqlalchemy
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
from sqlalchemy.orm.query import Query
from sqlalchemy.inspection import inspect

from zope.sqlalchemy import ZopeTransactionExtension

from clld.db.versioned import versioned_session
from clld.util import NO_DEFAULT, UnicodeMixin, format_json


@sqlalchemy.event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """Implements
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
    except:  # pragma: no cover
        # dispose the whole pool instead of invalidating one at a time
        connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise sqlalchemy.exc.DisconnectionError()
    cursor.close()


class ActiveOnlyQuery(Query):  # pragma: no cover
    """Implements a
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


def _solr_timestamp(dt):
    if not dt:
        return
    try:
        dt = dt.astimezone(UTC)
    except ValueError:
        pass
    return dt.isoformat().split('+')[0] + 'Z'


class _Base(UnicodeMixin):
    """The declarative base for all our models.
    """
    @declared_attr
    def __tablename__(cls):
        """We derive the table name from the model class name. This should be safe,
        because we don't want to have model classes with the same name either.
        Care has to be taken, though, to prevent collisions with the names of tables
        which are automatically created (history tables for example).
        """
        return cls.__name__.lower()

    #: All our models have an integer primary key which has nothing to do with
    #: the kind of data stored in a table. 'Natural' candidates for primary keys
    #: should be marked with unique constraints instead. This adds flexibility
    #: when it comes to database changes.
    pk = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    #: To allow for timestamp-based versioning - as opposed or in addition to the version
    #: number approach implemented in :py:class:`clld.db.meta.Versioned` - we store
    #: a timestamp for creation or an object.
    created = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True), default=datetime.utcnow)

    #: Timestamp for latest update of an object.
    updated = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    #: The active flag is meant as an easy way to mark records as obsolete or inactive,
    #: without actually deleting them. A custom Query class could then be used which
    #: filters out inactive records.
    active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    #: To allow storage of arbitrary key,value pairs with typed values, each model
    #: provides a column to store JSON encoded dicts.
    jsondata = sqlalchemy.Column(JSONEncodedDict)

    def update_jsondata(self, **kw):
        """Since we use the simple
        `JSON encoded dict recipe <http://docs.sqlalchemy.org/en/rel_0_9/core/types.html\
        #marshal-json-strings>`_
        without mutation tracking, we provide a convenience method to update
        """
        d = copy(self.jsondata) or {}
        d.update(**kw)
        self.jsondata = d

    @classmethod
    def mapper_name(cls):
        """To make implementing model class specific behavior across the technology
        boundary easier - e.g. specifying CSS classes - we provide a string representation
        of the model class.

        :rtype: str
        """
        return class_mapper(cls).class_.__name__

    @property
    def jsondatadict(self):
        return self.jsondata or {}

    @property
    def replacement_id(self):
        """This property is used to allow automatically redirecting to a 'better' version
        of a resource.
        """
        if not self.active:
            return self.jsondatadict.get('__replacement_id__')

    @classmethod
    def get(cls, value, key=None, default=NO_DEFAULT, session=None):
        """Convenient method to query a model where exactly one result is expected, e.g.
        to retrieve an instance by primary key or id.

        :param value: The value used in the filter expression of the query.
        :param str key: The key or attribute name to be used in the filter expression. If\
        None is passed, defaults to *pk* if value is ``int`` otherwise to *id*.
        """
        session = session or DBSession
        if key is None:
            key = 'pk' if isinstance(value, int) else 'id'
        try:
            return session.query(cls).filter_by(**{key: value}).one()
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
            return []  # pragma: no cover

        history_class = model.__history_mapper__.class_
        return DBSession.query(history_class).filter(history_class.pk == self.pk)\
            .order_by(sqlalchemy.desc(history_class.version))

    def __json__(self, req):
        """
        :param req: pyramid Request object.
        :return: ``dict`` suitable for serialization as JSON.
        """
        cols = []
        for om in object_mapper(self).iterate_to_root():
            cols.extend(col.key for col in om.local_table.c)

        return dict(
            (col, format_json(getattr(self, col)))
            for col in set(cols) if col not in ['created', 'updated', 'polymorphic_type'])

    def __solr__(self, req):
        """
        :param req: pyramid Request object.
        :return: ``dict`` suitable as JSON encoded \
        `Solr <https://lucene.apache.org/solr/>`_ document.

        .. note::

            The document returned by this method does only make sense when used with an
            appropriate Solr schema. In particular we rely on name conventions for
            `dynamic fields <https://cwiki.apache.org/confluence/display/solr/\
            Dynamic+Fields>`_.
        """
        cls = inspect(self).class_

        if not is_base(cls):
            for base in cls.__bases__:
                if is_base(base):
                    cls = base
                    break

        res = dict(
            id=getattr(self, 'id', str(self.pk)),
            url=req.resource_url(self) if req else None,
            dataset=req.dataset.id if req else None,
            rscname=cls.__name__,
            name=getattr(self, 'name', '%s %s' % (self.mapper_name(), self.pk)),
            active=self.active,
        )
        for attr in ['updated', 'created']:
            value = _solr_timestamp(getattr(self, attr))
            if value:
                res[attr] = value
        suffix_map = [(unicode, '_t'), (bool, '_b'), (int, '_i'), (float, '_f')]
        for om in object_mapper(self).iterate_to_root():
            for col in om.local_table.c:
                if col.key not in res and col.key != 'polymorphic_type':
                    value = getattr(self, col.key)
                    for type_, suffix in suffix_map:
                        if isinstance(value, type_):
                            res[col.key + suffix] = value
                            break
        return res

    def __unicode__(self):
        """
        :return: A human readable label for the object.
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


Base = declarative_base(cls=_Base)


class PolymorphicBaseMixin(object):
    """We use joined table inheritance to allow projects to augment base ``clld``
    models with project specific attributes. This mixin class prepares
    models to serve as base classes for inheritance.
    """
    polymorphic_type = sqlalchemy.Column(sqlalchemy.String(20))

    @declared_attr
    def __mapper_args__(cls):
        return {
            'polymorphic_on': cls.polymorphic_type,
            'polymorphic_identity': 'base',
            'with_polymorphic': '*',
        }


def is_base(cls):
    """
    :param cls: Model class.
    :return: ``bool`` signaling whether ``cls`` is a base class or derived, i.e.\
    customized.
    """
    # replace with inspection?
    # see http://docs.sqlalchemy.org/en/rel_0_9/orm/mapper_config.html
    #?highlight=polymorphic_identity#sqlalchemy.orm.mapper.Mapper.polymorphic_identity
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
