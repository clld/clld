from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld import interfaces

from . import (
    IdNameDescriptionMixin, DataMixin, HasDataMixin, FilesMixin, HasFilesMixin, Language)

__all__ = ('Unit',)


class Unit_data(Base, DataMixin):
    pass


class Unit_files(Base, FilesMixin):
    pass


@implementer(interfaces.IUnit)
class Unit(Base,
           PolymorphicBaseMixin,
           IdNameDescriptionMixin,
           HasDataMixin,
           HasFilesMixin):
    """A linguistic unit of a language."""

    __table_args__ = (UniqueConstraint('language_pk', 'id'),)

    language_pk = Column(Integer, ForeignKey('language.pk'), nullable=False)
    language = relationship(Language, innerjoin=True)
