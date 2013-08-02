"""
Common models for all clld apps
"""
from base64 import b64encode
from collections import OrderedDict
from datetime import date

from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    Boolean,
    Unicode,
    Date,
    LargeBinary,
    CheckConstraint,
    UniqueConstraint,
    ForeignKey,
    desc,
)
from sqlalchemy.orm import (
    relationship,
    validates,
    backref,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin, DBSession
from clld.db.versioned import Versioned
from clld import interfaces
from clld.util import DeclEnum
from clld.lib import bibtex
from clld.web.util.htmllib import HTML


#-----------------------------------------------------------------------------
# We augment mapper classes for basic objects using mixins to add the ability
# to store arbitrary key-value pairs and files associated with an object.
#-----------------------------------------------------------------------------
class Config(Base):
    key = Column(Unicode)
    value = Column(Unicode)


@implementer(interfaces.IFile)
class File(Base):
    """Model for storage of files in the database.
    """
    name = Column(Unicode)
    mime_type = Column(String)
    content = Column(LargeBinary)

    @hybrid_property
    def id(self):
        return self.pk

    def data_uri(self):
        return 'data:%s;base64,%s' % (self.mime_type, b64encode(self.content))


class FilesMixin(object):
    """This mixin provides a way to associate files with another model class.
    """
    @classmethod
    def owner_class(cls):
        return cls.__name__.split('_')[0]

    name = Column(Unicode)
    ord = Column(Integer, default=1)

    @declared_attr
    def file_pk(cls):
        return Column(Integer, ForeignKey('file.pk'))

    @declared_attr
    def file(cls):
        return relationship(File)

    @declared_attr
    def object_pk(cls):
        return Column(Integer, ForeignKey('%s.pk' % cls.owner_class().lower()))


class HasFilesMixin(object):
    """Adds a convenience method to retrieve a dict of associated files.

    .. note::

        It is the responsibility of the programmer to make sure conversion to a dict makes
        sense, i.e. the names of associated files are actually unique.
    """
    def filesdict(self):
        return dict((f.name, f.file) for f in self.files)

    @declared_attr
    def files(cls):
        return relationship(cls.__name__ + '_files')


class DataMixin(object):
    """This mixin provides a simple way to attach arbitrary key-value pairs to another
    model class identified by class name.
    """
    @classmethod
    def owner_class(cls):
        return cls.__name__.split('_')[0]

    key = Column(Unicode)
    value = Column(Unicode)
    ord = Column(Integer, default=1)

    @declared_attr
    def object_pk(cls):
        return Column(Integer, ForeignKey('%s.pk' % cls.owner_class().lower()))


class HasDataMixin(object):
    """Adds a convenience method to retrieve the key-value pairs from data as dict.

    .. note::

        It is the responsibility of the programmer to make sure conversion to a dict makes
        sense, i.e. the keys in data are actually unique.
    """
    def datadict(self):
        return dict((d.key, d.value) for d in self.data)

    @declared_attr
    def data(cls):
        return relationship(cls.__name__ + '_data', order_by=cls.__name__ + '_data.key')


class IdNameDescriptionMixin(object):
    """id is to be used as string identifier which can be used for sorting and as
    URL part.
    """
    id = Column(String, unique=True)
    name = Column(Unicode)
    description = Column(Unicode)
    markup_description = Column(Unicode)


class LanguageSource(Base, Versioned):
    __table_args__ = (UniqueConstraint('language_pk', 'source_pk'),)
    language_pk = Column(Integer, ForeignKey('language.pk'))
    source_pk = Column(Integer, ForeignKey('source.pk'))


#-----------------------------------------------------------------------------
# The mapper classes for basic objects of the clld db model are marked as
# implementers of the related interface.
#-----------------------------------------------------------------------------
class Dataset_data(Base, Versioned, DataMixin):
    pass


class Dataset_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IDataset)
class Dataset(Base,
              PolymorphicBaseMixin,
              Versioned,
              IdNameDescriptionMixin,
              HasDataMixin,
              HasFilesMixin):
    """Each project (e.g. WALS, APiCS) is regarded as one dataset; thus, each app will
    have exactly one Dataset object.
    """
    published = Column(Date, default=date.today)
    publisher_name = Column(
        Unicode, default=u"Max Planck Institute for Evolutionary Anthropology")
    publisher_place = Column(Unicode, default=u"Leipzig")
    publisher_url = Column(String, default="http://www.eva.mpg.de")
    license = Column(
        String, default="http://creativecommons.org/licenses/by-sa/3.0/")
    domain = Column(String, nullable=False)
    contact = Column(String)

    def get_stats(self, resources, **filters):
        res = OrderedDict()
        for rsc in resources:
            query = DBSession.query(rsc.model)
            if rsc.name in filters:
                query = query.filter(filters[rsc.name])
            res[rsc.name] = query.count()
        return res

    def formatted_editors(self):
        return ' & '.join(ed.contributor.last_first() for ed in self.editors)

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


class Language_data(Base, Versioned, DataMixin):
    pass


class Language_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.ILanguage)
class Language(Base,
               PolymorphicBaseMixin,
               Versioned,
               IdNameDescriptionMixin,
               HasDataMixin,
               HasFilesMixin):
    """Languages are the main objects of discourse. We attach a geo-coordinate
    to them to be able to put them on maps.
    """
    #__table_args__ = (UniqueConstraint('name'),)
    latitude = Column(
        Float(), CheckConstraint('-90 <= latitude and latitude <= 90'))
    longitude = Column(
        Float(), CheckConstraint('-180 <= longitude and longitude <= 180 '))
    identifiers = association_proxy('languageidentifier', 'identifier')

    def get_identifier(self, type_):
        for i in self.identifiers:
            if i.type == getattr(type_, 'value', type_):
                return i.name

    @property
    def iso_code(self):
        return self.get_identifier(IdentifierType.iso)


class DomainElement_data(Base, Versioned, DataMixin):
    pass


class DomainElement_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IDomainElement)
class DomainElement(Base,
                    PolymorphicBaseMixin,
                    Versioned,
                    IdNameDescriptionMixin,
                    HasDataMixin,
                    HasFilesMixin):
    """DomainElements can be used to model controlled lists of values for a Parameter.
    """
    __table_args__ = (
        UniqueConstraint('name', 'parameter_pk'),
        UniqueConstraint('number', 'parameter_pk'))

    parameter_pk = Column(Integer, ForeignKey('parameter.pk'))

    # the number is used to sort domain elements within the domain of one parameter
    number = Column(Integer)

    # abbreviated name, e.g. as label for map legends
    abbr = Column(Unicode)


class Parameter_data(Base, Versioned, DataMixin):
    pass


class Parameter_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IParameter)
class Parameter(Base,
                PolymorphicBaseMixin,
                Versioned,
                IdNameDescriptionMixin,
                HasDataMixin,
                HasFilesMixin):
    """A measurable attribute of a language.
    """
    __table_args__ = (UniqueConstraint('name'),)
    domain = relationship(
        'DomainElement', backref='parameter', order_by=DomainElement.number)


class Source_data(Base, Versioned, DataMixin):
    pass


class Source_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.ISource)
class Source(Base,
             PolymorphicBaseMixin,
             Versioned,
             IdNameDescriptionMixin,
             HasDataMixin,
             HasFilesMixin):
    """A bibliographic record, cited as source for some statement.
    """
    glottolog_id = Column(String)
    google_book_search_id = Column(String)

    #
    # BibTeX fields:
    #
    bibtex_type = Column(bibtex.EntryType.db_type())
    author = Column(Unicode)
    year = Column(Unicode)
    title = Column(Unicode)
    type = Column(Unicode)
    booktitle = Column(Unicode)
    editor = Column(Unicode)
    pages = Column(Unicode)
    edition = Column(Unicode)
    journal = Column(Unicode)
    school = Column(Unicode)
    address = Column(Unicode)
    url = Column(Unicode)
    note = Column(Unicode)
    number = Column(Unicode)
    series = Column(Unicode)
    volume = Column(Unicode)
    publisher = Column(Unicode)
    organization = Column(Unicode)
    chapter = Column(Unicode)
    howpublished = Column(Unicode)

    # typed information we might want to use for searching or sorting:
    year_int = Column(Integer)
    startpage_int = Column(Integer)
    pages_int = Column(Integer)

    languages = relationship(
        Language, backref='sources', secondary=LanguageSource.__table__)

    @property
    def gbs_identifier(self):
        #
        # TODO: remove hack after successful data import of glottolog 2
        #
        import json
        if isinstance(self.jsondata, basestring):
            self.jsondata = json.loads(self.jsondata)

        if not self.jsondata or not self.jsondata.get('gbs'):
            return
        if not self.jsondata['gbs']['volumeInfo'].get('industryIdentifiers'):
            return
        id_ = None
        for identifier in self.jsondata['gbs']['volumeInfo']['industryIdentifiers']:
            # prefer ISBN_13 over ISBN_10 over anything else
            if identifier['type'] == 'ISBN_13':
                id_ = 'ISBN:' + identifier['identifier']
            if identifier['type'] == 'ISBN_10' and not id_:
                id_ = 'ISBN:' + identifier['identifier']
        if not id_:
            # grab the last one in the list (most probably the only one!)
            id_ = identifier['identifier']
        return id_

    def bibtex(self):
        return bibtex.Record.from_object(self)


class Contribution_data(Base, Versioned, DataMixin):
    pass


class Contribution_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IContribution)
class Contribution(Base,
                   PolymorphicBaseMixin,
                   Versioned,
                   IdNameDescriptionMixin,
                   HasDataMixin,
                   HasFilesMixin):
    """A set of data contributed within the same context by the same set of contributors.
    """
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


class ValueSet_data(Base, Versioned, DataMixin):
    pass


class ValueSet_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IValueSet)
class ValueSet(Base,
               PolymorphicBaseMixin,
               Versioned,
               IdNameDescriptionMixin,
               HasDataMixin,
               HasFilesMixin):
    """The intersection of Language and Parameter.
    """
    language_pk = Column(Integer, ForeignKey('language.pk'))
    parameter_pk = Column(Integer, ForeignKey('parameter.pk'))
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    source = Column(Unicode)

    parameter = relationship('Parameter', backref='valuesets')
    contribution = relationship('Contribution', backref='valuesets')

    @declared_attr
    def language(cls):
        return relationship(
            'Language', backref=backref('valuesets', order_by=cls.language_pk))

    @property
    def name(self):
        return self.language.name + ' / ' + self.parameter.name


class Value_data(Base, Versioned, DataMixin):
    pass


class Value_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IValue)
class Value(Base,
            PolymorphicBaseMixin,
            Versioned,
            IdNameDescriptionMixin,
            HasDataMixin,
            HasFilesMixin):
    """A measurement of a parameter for a particular language.
    """
    # we must override the pk col declaration from Base to have it available for ordering.
    pk = Column(Integer, primary_key=True)
    valueset_pk = Column(Integer, ForeignKey('valueset.pk'))
    # Values may be taken from a domain.
    domainelement_pk = Column(Integer, ForeignKey('domainelement.pk'))

    # Languages may have multiple values for the same parameter. Their relative
    # frequency can be stored here.
    frequency = Column(Float)
    confidence = Column(Unicode)

    domainelement = relationship('DomainElement', backref='values')

    @declared_attr
    def valueset(cls):
        return relationship(
            ValueSet,
            backref=backref(
                'values', order_by=[desc(cls.frequency), cls.confidence, cls.pk]))

    def __json__(self, req):
        res = Base.__json__(self, req)
        res['domainelement'] = self.domainelement.__json__(req) \
            if self.domainelement else None
        res['valueset'] = self.valueset.__json__(req)
        return res

    def __unicode__(self):
        return self.domainelement.name if self.domainelement else self.name or self.id


class Contributor_data(Base, Versioned, DataMixin):
    pass


class Contributor_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IContributor)
class Contributor(Base,
                  PolymorphicBaseMixin,
                  Versioned,
                  IdNameDescriptionMixin,
                  HasDataMixin,
                  HasFilesMixin):
    """Creator of a contribution.
    """
    __table_args__ = (UniqueConstraint('name'),)
    url = Column(Unicode())
    email = Column(String)
    address = Column(Unicode)

    def last_first(self):
        """ad hoc - possibly incorrect - way of formatting the name as "last, first"
        """
        parts = (self.name or '').split()
        return '' if not parts else ', '.join([parts[-1], ' '.join(parts[:-1])])


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
    """A linguistic unit of a language.
    """
    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(Language)


class UnitDomainElement_data(Base, Versioned, DataMixin):
    pass


class UnitDomainElement_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IUnitDomainElement)
class UnitDomainElement(Base,
                        PolymorphicBaseMixin,
                        Versioned,
                        IdNameDescriptionMixin,
                        HasDataMixin,
                        HasFilesMixin):
    unitparameter_pk = Column(Integer, ForeignKey('unitparameter.pk'))
    ord = Column(Integer)

    # do we need a numeric value for these?


class UnitParameter_data(Base, Versioned, DataMixin):
    pass


class UnitParameter_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IUnitParameter)
class UnitParameter(Base,
                    PolymorphicBaseMixin,
                    Versioned,
                    IdNameDescriptionMixin,
                    HasDataMixin,
                    HasFilesMixin):
    """A measurable attribute of a unit.
    """
    domain = relationship(
        'UnitDomainElement', backref='parameter', order_by=UnitDomainElement.id)


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
    unit_pk = Column(Integer, ForeignKey('unit.pk'))
    unitparameter_pk = Column(Integer, ForeignKey('unitparameter.pk'))
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))

    # Values may be taken from a domain.
    unitdomainelement_pk = Column(Integer, ForeignKey('unitdomainelement.pk'))

    # Languages may have multiple values for the same parameter. Their relative
    # frequency can be stored here.
    frequency = Column(Float)

    unitparameter = relationship('UnitParameter', backref='unitvalues')
    unitdomainelement = relationship('UnitDomainElement', backref='unitvalues')
    contribution = relationship('Contribution', backref='unitvalues')

    @declared_attr
    def unit(cls):
        return relationship('Unit', backref=backref('unitvalues', order_by=cls.unit_pk))

    @validates('unitparameter_pk')
    def validate_parameter_pk(self, key, unitparameter_pk):
        """We have to make sure, the parameter a value is tied to and the parameter a
        possible domainelement is tied to stay in sync.
        """
        if self.unitdomainelement and self.unitdomainelement.unitparameter_pk:
            assert self.unitdomainelement.unitparameter_pk == unitparameter_pk
        return unitparameter_pk

    def __unicode__(self):
        return self.unitdomainelement.name \
            if self.unitdomainelement else self.name or self.id


#-----------------------------------------------------------------------------
# Non-core mappers and association tables
#-----------------------------------------------------------------------------
class GlossAbbreviation(Base, Versioned, IdNameDescriptionMixin):
    __table_args__ = (UniqueConstraint('id', 'language_pk'),)

    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(Language, backref="gloss_abbreviations")


class IdentifierType(DeclEnum):
    iso = 'iso639-3', 'ISO 639-3'
    wals = 'wals', 'WALS Code'
    glottolog = 'glottolog', 'Glottocode'


class Identifier(Base, Versioned, IdNameDescriptionMixin):
    """We want to be able to link languages to languages in other systems. Thus,
    we store identifiers of various types like 'wals', 'iso639-3', 'glottolog'.
    But we might as well just store alternative names for languages.
    """
    __table_args__ = (UniqueConstraint('name', 'type', 'description'),)
    id = Column(String)
    type = Column(String)
    lang = Column(String(3), default='en')


class LanguageIdentifier(Base, Versioned):
    """Languages are linked to identifiers with an optional description of this
    linkage, e.g. 'is dialect of'.
    """
    language_pk = Column(Integer, ForeignKey('language.pk'))
    identifier_pk = Column(Integer, ForeignKey('identifier.pk'))
    description = Column(Unicode)

    identifier = relationship(Identifier)
    language = relationship(
        Language,
        backref=backref("languageidentifier", cascade="all, delete-orphan"))


#
# Several objects can be linked to sources, i.e. they can have references.
#
class HasSourceMixin(object):
    key = Column(Unicode)  # the citation key, specific (and unique) within a contribution
    description = Column(Unicode)  # e.g. page numbers.

    @declared_attr
    def source_pk(cls):
        return Column(Integer, ForeignKey('source.pk'))

    @declared_attr
    def source(cls):
        return relationship(Source, backref=cls.__name__.lower() + 's')


class SentenceReference(Base, Versioned, HasSourceMixin):
    """
    """
    sentence_pk = Column(Integer, ForeignKey('sentence.pk'))
    sentence = relationship(Sentence, backref="references")


class ContributionReference(Base, Versioned, HasSourceMixin):
    """
    """
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contribution = relationship(Contribution, backref="references")


class ValueSetReference(Base, Versioned, HasSourceMixin):
    """References for a set of values (related to one parameter and one language).

    These references can be interpreted as justifications why a language does not "have"
    certain values for a parameter, too.
    """
    valueset_pk = Column(Integer, ForeignKey('valueset.pk'))
    valueset = relationship(ValueSet, backref="references")


class ContributionContributor(Base, PolymorphicBaseMixin, Versioned):
    """Many-to-many association between contributors and contributions
    """
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contributor_pk = Column(Integer, ForeignKey('contributor.pk'))

    # contributors are ordered.
    ord = Column(Integer, default=1)

    # we distinguish between primary and secondary (a.k.a. 'with ...') contributors.
    primary = Column(Boolean, default=True)

    contribution = relationship(Contribution, backref='contributor_assocs')
    contributor = relationship(Contributor, lazy=False, backref='contribution_assocs')


class Editor(Base, PolymorphicBaseMixin, Versioned):
    """Many-to-many association between contributors and dataset
    """
    dataset_pk = Column(Integer, ForeignKey('dataset.pk'))
    contributor_pk = Column(Integer, ForeignKey('contributor.pk'))

    # contributors are ordered.
    ord = Column(Integer, default=1)

    # we distinguish between primary and secondary (a.k.a. 'with ...') contributors.
    primary = Column(Boolean, default=True)

    contributor = relationship(Contributor, lazy=False)

    @declared_attr
    def dataset(cls):
        return relationship(
            Dataset, backref=backref(
                'editors', order_by=[cls.primary, cls.ord], lazy=False))


class ValueSentence(Base, PolymorphicBaseMixin, Versioned):
    """Many-to-many association between values and sentences given as explanation of a
    value.
    """
    value_pk = Column(Integer, ForeignKey('value.pk'))
    sentence_pk = Column(Integer, ForeignKey('sentence.pk'))
    description = Column(Unicode())

    value = relationship(Value, backref='sentence_assocs')
    sentence = relationship(Sentence, backref='value_assocs', order_by=Sentence.id)


class UnitParameterUnit(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin):
    unit_pk = Column(Integer, ForeignKey('unit.pk'))
    unitparameter_pk = Column(Integer, ForeignKey('unitparameter.pk'))
    unit = relationship(Unit, backref='unitparameter_assocs')
    unitparameter = relationship(UnitParameter, backref='unit_assocs')
