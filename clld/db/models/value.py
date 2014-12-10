from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import (
    Column,
    Float,
    Integer,
    Unicode,
    ForeignKey,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin,
    Sentence, ValueSet,
    parameter as _parameter)  # needed to initalize relationship
assert _parameter

__all__ = ('Value', 'ValueSentence')


class Value_data(Base, Versioned, DataMixin):
    pass


class Value_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IValue)
class Value(Base,
            PolymorphicBaseMixin,
            Versioned,
            IdNameDescriptionMixin,
            HasDataMixin,
            HasFilesMixin):

    """A measurement of a parameter for a particular language."""

    # we must override the pk col declaration from Base to have it available for ordering.
    pk = Column(Integer, primary_key=True)
    valueset_pk = Column(Integer, ForeignKey('valueset.pk'))
    # Values may be taken from a domain.
    domainelement_pk = Column(Integer, ForeignKey('domainelement.pk'))

    frequency = Column(
        Float,
        doc='frequency of the value relative to other values for the same language')
    """Languages may have multiple values for the same parameter. Their relative
    frequency can be stored here."""
    confidence = Column(
        Unicode, doc='textual assessment of the reliability of the value assignment')

    domainelement = relationship('DomainElement', backref='values')

    @declared_attr
    def valueset(cls):
        return relationship(
            ValueSet,
            backref=backref(
                'values', order_by=[cls.frequency.desc(), cls.confidence, cls.pk]))

    def __json__(self, req):
        res = Base.__json__(self, req)
        res['domainelement'] = self.domainelement.__json__(req) \
            if self.domainelement else None
        res['valueset'] = self.valueset.__json__(req)
        return res

    def __unicode__(self):
        return self.domainelement.name if self.domainelement else self.name or self.id


class ValueSentence(Base, PolymorphicBaseMixin, Versioned):

    """Association between values and sentences given as explanation of a value."""

    value_pk = Column(Integer, ForeignKey('value.pk'))
    sentence_pk = Column(Integer, ForeignKey('sentence.pk'))
    description = Column(Unicode())

    value = relationship(Value, backref='sentence_assocs')
    sentence = relationship(Sentence, backref='value_assocs', order_by=Sentence.id)
