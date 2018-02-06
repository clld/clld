from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import Column, Integer, Unicode, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref, joinedload
from sqlalchemy.ext.declarative import declared_attr

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin,
    HasSourceNotNullMixin,
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

    """The intersection of Language, Parameter, and optionally Contribution."""

    __table_args__ = (
        UniqueConstraint('language_pk', 'parameter_pk', 'contribution_pk'),
    )

    language_pk = Column(Integer, ForeignKey('language.pk'), nullable=False)
    parameter_pk = Column(Integer, ForeignKey('parameter.pk'), nullable=False)
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    source = Column(Unicode, doc='textual description of the source for the valueset')

    parameter = relationship('Parameter', innerjoin=True, backref='valuesets')

    @staticmethod
    def refine_factory_query(query):
        return query.options(
            joinedload(ValueSet.values),
            joinedload(ValueSet.parameter),
            joinedload(ValueSet.language),
        )

    @declared_attr
    def contribution(cls):
        return relationship(
            'Contribution', backref=backref('valuesets', order_by=cls.parameter_pk))

    @declared_attr
    def language(cls):
        return relationship(
            'Language', innerjoin=True, backref=backref('valuesets', order_by=cls.language_pk))

    @property
    def name(self):
        return self.language.name + ' / ' + self.parameter.name


class ValueSetReference(Base, Versioned, HasSourceNotNullMixin):

    """References for a set of values (related to one parameter and one language).

    These references can be interpreted as justifications why a language does not "have"
    certain values for a parameter, too.
    """

    __table_args__ = (UniqueConstraint('valueset_pk', 'source_pk', 'description'),)

    valueset_pk = Column(Integer, ForeignKey('valueset.pk'), nullable=False)
    valueset = relationship(ValueSet, innerjoin=True, backref="references")
