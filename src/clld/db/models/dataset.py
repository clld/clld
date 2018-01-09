from __future__ import unicode_literals, print_function, division, absolute_import

from collections import OrderedDict
from datetime import date

from sqlalchemy import (
    Column, String, Unicode, Date, Integer, ForeignKey, Boolean,
    UniqueConstraint)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin, DBSession
from clld.db.versioned import Versioned
from clld import interfaces
from clld.web.util.htmllib import HTML

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin,
    Contributor)

__all__ = ('Dataset', 'Editor')


class Dataset_data(Base, Versioned, DataMixin):

    """Associated data mapper."""


class Dataset_files(Base, Versioned, FilesMixin):

    """Associated files mapper."""


@implementer(interfaces.IDataset)
class Dataset(Base,
              PolymorphicBaseMixin,
              Versioned,
              IdNameDescriptionMixin,
              HasDataMixin,
              HasFilesMixin):

    """Represents a database.

    Each project (e.g. WALS, APiCS) is regarded as one dataset; thus, each app will
    have exactly one Dataset object.
    """

    published = Column(Date, default=date.today, doc='date of publication')
    publisher_name = Column(Unicode, doc='publisher')
    publisher_place = Column(Unicode, doc='place of publication')
    publisher_url = Column(String)
    license = Column(String, default="http://creativecommons.org/licenses/by/3.0/")
    domain = Column(String, nullable=False)
    contact = Column(String)

    def get_stats(self, resources, **filters):
        res = OrderedDict()
        for rsc in resources:
            if rsc.name != 'combination':
                query = DBSession.query(rsc.model)
                if rsc.name in filters:
                    query = query.filter(filters[rsc.name])
                res[rsc.name] = query.count()
        return res

    def formatted_editors(self):
        def _format(eds):
            return ' & '.join(ed.contributor.last_first() for ed in eds)

        res = _format([e for e in self.editors if e.primary])
        secondary = [e for e in self.editors if not e.primary]
        if secondary:
            res = ' with '.join([res, _format(secondary)])  # pragma: no cover
        return res

    def formatted_name(self):
        return HTML.span(
            self.name,
            **{
                'xmlns:dct': "http://purl.org/dc/terms/",
                'href': "http://purl.org/dc/dcmitype/Dataset",
                'property': "dct:title",
                'rel': "dct:type",
                'class': 'Dataset'}
        )


class Editor(Base, PolymorphicBaseMixin, Versioned):

    """Many-to-many association between contributors and dataset."""

    __table_args__ = (UniqueConstraint('dataset_pk', 'contributor_pk'),)

    dataset_pk = Column(Integer, ForeignKey('dataset.pk'), nullable=False)
    contributor_pk = Column(Integer, ForeignKey('contributor.pk'), nullable=False)

    # contributors are ordered.
    ord = Column(Integer, default=1)

    # we distinguish between primary and secondary (a.k.a. 'with ...') contributors.
    primary = Column(Boolean, default=True)

    contributor = relationship(
        Contributor, innerjoin=True, lazy=False, backref=backref('editor', uselist=False))

    @declared_attr
    def dataset(cls):
        return relationship(
            Dataset, innerjoin=True, backref=backref(
                'editors', order_by=[cls.primary.desc(), cls.ord], lazy=False))
