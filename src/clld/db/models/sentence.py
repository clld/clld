from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import Column, Integer, Unicode, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin, HasSourceNotNullMixin)

__all__ = ('Sentence', 'SentenceReference')


class Sentence_data(Base, Versioned, DataMixin):
    pass


class Sentence_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.ISentence)
class Sentence(Base,
               PolymorphicBaseMixin,
               Versioned,
               IdNameDescriptionMixin,
               HasDataMixin,
               HasFilesMixin):

    """Sentence of a language serving as example for some statement.

    .. note::

        Columns inherited from IdNameDescriptionMixin are interpreted as follows:

            name: The text of the sentence in object language
            description: A translation of the sentence

        Columns with a name prefix of 'markup_' can be used to store data containing HTML
        markup. These attributes should take precedence over their non-prefixed
        counterparts when rendering a Sentence.
    """

    analyzed = Column(Unicode)
    gloss = Column(Unicode)
    type = Column(Unicode)
    source = Column(Unicode)
    comment = Column(Unicode)
    original_script = Column(Unicode)
    xhtml = Column(Unicode)

    markup_text = Column(Unicode)
    markup_analyzed = Column(Unicode)
    markup_gloss = Column(Unicode)
    markup_comment = Column(Unicode)

    language_pk = Column(Integer, ForeignKey('language.pk'))

    @declared_attr
    def language(cls):
        return relationship(
            'Language', backref=backref('sentences', order_by=cls.language_pk))

    @property
    def audio(self):
        for f in self._files:
            if f.mime_type.split('/')[0] == 'audio':
                return f


class SentenceReference(Base, Versioned, HasSourceNotNullMixin):

    """Association table."""

    __table_args__ = (
        UniqueConstraint('sentence_pk', 'source_pk', 'description'),
    )

    sentence_pk = Column(Integer, ForeignKey('sentence.pk'), nullable=False)
    sentence = relationship(Sentence, innerjoin=True, backref="references")
