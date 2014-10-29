from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin,
    Language, _add_solr_language_info)

__all__ = ('Unit',)


class Unit_data(Base, Versioned, DataMixin):
    pass


class Unit_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IUnit)
class Unit(Base,
           PolymorphicBaseMixin,
           Versioned,
           IdNameDescriptionMixin,
           HasDataMixin,
           HasFilesMixin):

    """A linguistic unit of a language."""

    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(Language)

    def __solr__(self, req):
        return _add_solr_language_info(Base.__solr__(self, req), self)
