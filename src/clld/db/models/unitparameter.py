from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld import interfaces

from . import IdNameDescriptionMixin, DataMixin, HasDataMixin, FilesMixin, HasFilesMixin

__all__ = ('UnitDomainElement', 'UnitParameter')


class UnitDomainElement_data(Base, DataMixin):
    pass


class UnitDomainElement_files(Base, FilesMixin):
    pass


@implementer(interfaces.IUnitDomainElement)
class UnitDomainElement(Base,
                        PolymorphicBaseMixin,
                        IdNameDescriptionMixin,
                        HasDataMixin,
                        HasFilesMixin):

    """Domain element for the domain of a UnitParameter."""

    __table_args__ = (
        UniqueConstraint('unitparameter_pk', 'name'),
        UniqueConstraint('unitparameter_pk', 'ord'),
    )

    unitparameter_pk = Column(Integer, ForeignKey('unitparameter.pk'), nullable=False)
    ord = Column(Integer)

    def url(self, request):
        return request.resource_url(self.parameter, _anchor='DE-%s' % self.id)


class UnitParameter_data(Base, DataMixin):
    pass


class UnitParameter_files(Base, FilesMixin):
    pass


@implementer(interfaces.IUnitParameter)
class UnitParameter(Base,
                    PolymorphicBaseMixin,
                    IdNameDescriptionMixin,
                    HasDataMixin,
                    HasFilesMixin):

    """A measurable attribute of a unit."""

    domain = relationship(
        'UnitDomainElement', backref='parameter', order_by=UnitDomainElement.id)
