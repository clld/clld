from sqlalchemy import Column, String, Unicode, UniqueConstraint

from zope.interface import implementer
from nameparser import HumanName

from clld.db.meta import Base, PolymorphicBaseMixin
from clld import interfaces

from .import (
    IdNameDescriptionMixin,
    DataMixin, FilesMixin, HasDataMixin, HasFilesMixin)

__all__ = ('Contributor',)


class Contributor_data(Base, DataMixin):
    pass


class Contributor_files(Base, FilesMixin):
    pass


@implementer(interfaces.IContributor)
class Contributor(Base,
                  PolymorphicBaseMixin,
                  IdNameDescriptionMixin,
                  HasDataMixin,
                  HasFilesMixin):

    """Creator of a contribution."""

    __table_args__ = (UniqueConstraint('name'),)

    url = Column(Unicode())
    email = Column(String)
    address = Column(Unicode)

    def last_first(self):
        if not self.name:
            return ''
        return '{0.last}, {0.first} {0.middle}'.format(HumanName(self.name)).strip()
