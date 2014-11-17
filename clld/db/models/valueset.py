from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import Column, Integer, Unicode, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin,
    HasSourceMixin,
    parameter as _parameter)  # needed to initalize relationship
assert _parameter

__all__ = ('ValueSet', 'ValueSetReference')


class ValueSet_data(Base, Versioned, DataMixin):
    pass


class ValueSet_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IValueSet)
class ValueSet(Base,
               PolymorphicBaseMixin,
               Versioned,
               IdNameDescriptionMixin,
               HasDataMixin,
               HasFilesMixin):

    """The intersection of Language and Parameter."""

    language_pk = Column(Integer, ForeignKey('language.pk'))
    parameter_pk = Column(Integer, ForeignKey('parameter.pk'))
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    source = Column(Unicode, doc='textual description of the source for the valueset')

    parameter = relationship('Parameter', backref='valuesets')

    @declared_attr
    def contribution(cls):
        return relationship(
            'Contribution', backref=backref('valuesets', order_by=cls.parameter_pk))

    @declared_attr
    def language(cls):
        return relationship(
            'Language', backref=backref('valuesets', order_by=cls.language_pk))

    @property
    def name(self):
        return self.language.name + ' / ' + self.parameter.name


class ValueSetReference(Base, Versioned, HasSourceMixin):

    """References for a set of values (related to one parameter and one language).

    These references can be interpreted as justifications why a language does not "have"
    certain values for a parameter, too.
    """

    valueset_pk = Column(Integer, ForeignKey('valueset.pk'))
    valueset = relationship(ValueSet, backref="references")
