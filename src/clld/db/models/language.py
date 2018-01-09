from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    Unicode,
    CheckConstraint,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces
from clld.util import DeclEnum

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin)

__all__ = (
    'Language', 'LanguageSource',
    'IdentifierType', 'Identifier', 'LanguageIdentifier',
)


class Language_data(Base, Versioned, DataMixin):

    """Associated data mapper."""


class Language_files(Base, Versioned, FilesMixin):

    """Associated files mapper."""


@implementer(interfaces.ILanguage)
class Language(Base,
               PolymorphicBaseMixin,
               Versioned,
               IdNameDescriptionMixin,
               HasDataMixin,
               HasFilesMixin):

    """Languages are the main objects of discourse.

    We attach a geo-coordinate to them to be able to put them on maps.
    """

    latitude = Column(
        Float(),
        CheckConstraint('-90 <= latitude and latitude <= 90'),
        doc='geographical latitude in WGS84')
    longitude = Column(
        Float(),
        CheckConstraint('-180 <= longitude and longitude <= 180 '),
        doc='geographical longitude in WGS84')
    identifiers = association_proxy('languageidentifier', 'identifier')

    def get_identifier_objs(self, type_):
        return [i for i in self.identifiers if i.type == getattr(type_, 'value', type_)]

    def get_identifier(self, type_):
        objs = self.get_identifier_objs(type_)
        if objs:
            return objs[0].name

    @property
    def iso_code(self):
        return self.get_identifier(IdentifierType.iso)

    @property
    def glottocode(self):
        return self.get_identifier(IdentifierType.glottolog)


class LanguageSource(Base, Versioned):

    """Association table."""

    __table_args__ = (UniqueConstraint('language_pk', 'source_pk'),)

    language_pk = Column(Integer, ForeignKey('language.pk'), nullable=False)
    source_pk = Column(Integer, ForeignKey('source.pk'), nullable=False)


class IdentifierType(DeclEnum):

    """Known language identifiers."""

    iso = 'iso639-3', 'ISO 639-3', \
          'http://www-01.sil.org/iso639-3/documentation.asp?id={0.name}'
    wals = 'wals', 'WALS Code', 'http://wals.info/languoid/lect/wals_code_{0.name}'
    glottolog = 'glottolog', 'Glottocode', \
                'http://glottolog.org/resource/languoid/id/{0.name}'
    ethnologue = 'ethnologue', 'Ethnologue', 'http://www.ethnologue.com/language/{0.name}'


class Identifier(Base, Versioned, IdNameDescriptionMixin):

    """A language identifier.

    We want to be able to link languages to languages in other systems. Thus,
    we store identifiers of various types like 'wals', 'iso639-3', 'glottolog'.
    But we might as well just store alternative names for languages.
    """

    __table_args__ = (UniqueConstraint('name', 'type', 'description', 'lang'),)

    id = Column(String)
    type = Column(String)
    lang = Column(String(3), default='en')

    def url(self):
        try:
            return IdentifierType.from_string(self.type).args[0].format(self)
        except ValueError:
            return


class LanguageIdentifier(Base, Versioned):

    """Association table.

    Languages are linked to identifiers with an optional description of this
    linkage, e.g. 'is dialect of'.
    """

    __table_args__ = (UniqueConstraint('language_pk', 'identifier_pk'),)

    language_pk = Column(Integer, ForeignKey('language.pk'), nullable=False)
    identifier_pk = Column(Integer, ForeignKey('identifier.pk'), nullable=False)
    description = Column(Unicode)

    identifier = relationship(Identifier, innerjoin=True)
    language = relationship(
        Language, innerjoin=True,
        backref=backref("languageidentifier", cascade="all, delete-orphan"))
