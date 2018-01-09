from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import Column, Float, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, validates, backref
from sqlalchemy.ext.declarative import declared_attr

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin,
    unitparameter as _unitparameter)  # needed to initalize relationship
assert _unitparameter

__all__ = ('UnitValue',)


class UnitValue_data(Base, Versioned, DataMixin):
    pass


class UnitValue_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IUnitValue)
class UnitValue(Base,
                PolymorphicBaseMixin,
                Versioned,
                IdNameDescriptionMixin,
                HasDataMixin,
                HasFilesMixin):

    __table_args__ = (UniqueConstraint(
        'unit_pk', 'unitparameter_pk', 'contribution_pk', 'name', 'unitdomainelement_pk'),
    )

    unit_pk = Column(Integer, ForeignKey('unit.pk'), nullable=False)
    unitparameter_pk = Column(Integer, ForeignKey('unitparameter.pk'), nullable=False)
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))

    # Values may be taken from a domain.
    unitdomainelement_pk = Column(Integer, ForeignKey('unitdomainelement.pk'))

    # Languages may have multiple values for the same parameter. Their relative
    # frequency can be stored here.
    frequency = Column(Float)

    unitparameter = relationship('UnitParameter', innerjoin=True, backref='unitvalues')
    unitdomainelement = relationship('UnitDomainElement', backref='unitvalues')
    contribution = relationship('Contribution', backref='unitvalues')

    @declared_attr
    def unit(cls):
        return relationship(
            'Unit', innerjoin=True, backref=backref('unitvalues', order_by=cls.unit_pk))

    @validates('unitparameter_pk')
    def validate_parameter_pk(self, key, unitparameter_pk):
        """Validator to sync related parameter.

        We have to make sure, the parameter a value is tied to and the parameter a
        possible domainelement is tied to stay in sync.
        """
        if self.unitdomainelement and self.unitdomainelement.unitparameter_pk:
            assert self.unitdomainelement.unitparameter_pk == unitparameter_pk
        return unitparameter_pk

    def __unicode__(self):
        return self.unitdomainelement.name \
            if self.unitdomainelement else self.name or self.id


#
# TODO: UnitValueSentence!
#
