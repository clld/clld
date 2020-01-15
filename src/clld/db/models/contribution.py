from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld import interfaces

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin,
    HasSourceNotNullMixin, Contributor)

__all__ = ('Contribution', 'ContributionReference', 'ContributionContributor')


class Contribution_data(Base, DataMixin):
    pass


class Contribution_files(Base, FilesMixin):
    pass


@implementer(interfaces.IContribution)
class Contribution(Base,
                   PolymorphicBaseMixin,
                   IdNameDescriptionMixin,
                   HasDataMixin,
                   HasFilesMixin):

    """A set of data contributed within the same context by the same contributors."""

    __table_args__ = (UniqueConstraint('name'),)

    date = Column(Date)

    @property
    def primary_contributors(self):
        return [assoc.contributor for assoc in
                sorted(self.contributor_assocs,
                       key=lambda a: (a.ord, a.contributor.id)) if assoc.primary]

    @property
    def secondary_contributors(self):
        return [assoc.contributor for assoc in
                sorted(self.contributor_assocs,
                       key=lambda a: (a.ord, a.contributor.id)) if not assoc.primary]

    def formatted_contributors(self):
        contribs = [' and '.join(c.name for c in self.primary_contributors)]
        if self.secondary_contributors:
            contribs.append(' and '.join(c.name for c in self.secondary_contributors))
        return ' with '.join(contribs)


class ContributionReference(Base, HasSourceNotNullMixin):

    """Association table."""

    __table_args__ = (
        UniqueConstraint('contribution_pk', 'source_pk', 'description'),
    )

    contribution_pk = Column(Integer, ForeignKey('contribution.pk'), nullable=False)
    contribution = relationship(Contribution, innerjoin=True, backref="references")


class ContributionContributor(Base, PolymorphicBaseMixin):

    """Many-to-many association between contributors and contributions."""

    __table_args__ = (UniqueConstraint('contribution_pk', 'contributor_pk'),)

    contribution_pk = Column(Integer, ForeignKey('contribution.pk'), nullable=False)
    contributor_pk = Column(Integer, ForeignKey('contributor.pk'), nullable=False)

    # contributors are ordered.
    ord = Column(Integer, default=1)

    # we distinguish between primary and secondary (a.k.a. 'with ...') contributors.
    primary = Column(Boolean, default=True)

    contribution = relationship(
        Contribution, innerjoin=True, backref='contributor_assocs')
    contributor = relationship(
        Contributor, innerjoin=True, lazy=False, backref='contribution_assocs')
