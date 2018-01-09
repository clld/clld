from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import Column, Integer, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

from clld.db.meta import Base
from clld.db.versioned import Versioned

from . import IdNameDescriptionMixin, Language

__all__ = ('GlossAbbreviation',)


class GlossAbbreviation(Base, Versioned, IdNameDescriptionMixin):

    """Possibly language-specific abbreviation used in IGTs."""

    __table_args__ = (UniqueConstraint('id', 'language_pk'),)

    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(Language, backref="gloss_abbreviations")
