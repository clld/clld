"""
Common models for all clld apps
"""
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
    and_,
    desc,
)
from sqlalchemy.orm import (
    relationship,
    validates,
    backref,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces


#
# TODO: relations to data and files!
#
"""
http://chart.googleapis.com/chart?cht=p&chs=38x38&chd=t:60,40&chco=FF0000|00FF00&chf=bg,s,FFFFFF00

note: deprecated; only works until april 2015!

chs: 38px charts result in the pie having a diameter of about 17px
chd: series of numbers
chco: colors per slice
chf: make sure backgroud is transparent (the 00 added to the color spec)
"""


#-----------------------------------------------------------------------------
# We augment mapper classes for basic objects using mixins to add the ability
# to store arbitrary key-value pairs and files associated with an object.
#-----------------------------------------------------------------------------
class Config(Base):
    key = Column(Unicode)
    value = Column(Unicode)


class File(Base):
    """Model for storage of files in the database.
    """
    name = Column(Unicode)
    mime_type = Column(String)
    content = Column(LargeBinary)


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

    #@declared_attr
    #def object(cls):
    #    return relationship(cls.owner_class(), backref=backref('files', order_by=cls.ord))


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
        return relationship(cls.__name__ + '_data')


class IdNameDescriptionMixin(object):
    """id is to be used as string identifier which can be used for sorting and as
    URL part.
    """
    id = Column(String, unique=True)
    name = Column(Unicode)
    description = Column(Unicode)


#-----------------------------------------------------------------------------
# The mapper classes for basic objects of the clld db model are marked as
# implementers of the related interface.
#-----------------------------------------------------------------------------
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
    __table_args__ = (UniqueConstraint('name'),)
    latitude = Column(Float(), CheckConstraint('-90 <= latitude and latitude <= 90'))
    longitude = Column(Float(), CheckConstraint('-180 <= longitude and longitude <= 180 '))
    identifiers = association_proxy('languageidentifier', 'identifier')
    sources = association_proxy('languagesource', 'source')


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
    number = Column(Integer)


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
    domain = relationship('DomainElement', backref='parameter', order_by=DomainElement.id)


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
    authors = Column(Unicode)
    year = Column(Unicode)

    glottolog_id = Column(String)
    google_book_search_id = Column(String)

    languages = association_proxy('languagesource', 'language')


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
                sorted(self.contributor_assocs, key=lambda a: (a.ord, a.contributor.id)) if assoc.primary]

    @property
    def secondary_contributors(self):
        return [assoc.contributor for assoc in
                sorted(self.contributor_assocs, key=lambda a: (a.ord, a.contributor.id)) if not assoc.primary]


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
        res['domainelement'] = self.domainelement.__json__(req)
        res['valueset'] = self.valueset.__json__(req)
        return res


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
    source = Column(Unicode)
    comment = Column(Unicode)
    original_script = Column(Unicode)
    xhtml = Column(Unicode)

    language_pk = Column(Integer, ForeignKey('language.pk'))

    @declared_attr
    def language(cls):
        return relationship('Language', backref=backref('sentences', order_by=cls.language_pk))


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
        if self.unitdomainelement:
            assert self.unitdomainelement.unitparameter_pk == unitparameter_pk
        return unitparameter_pk


#-----------------------------------------------------------------------------
# Non-core mappers and association tables
#-----------------------------------------------------------------------------
class GlossAbbreviation(Base, Versioned, IdNameDescriptionMixin):
    __table_args__ = (UniqueConstraint('id', 'language_pk'),)

    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(Language, backref="gloss_abbreviations")


class Identifier(Base, Versioned, IdNameDescriptionMixin):
    """We want to be able to link languages to languages in other systems. Thus,
    we store identifiers of various types like 'wals', 'iso639-3', 'glottolog'.
    But we might as well just store alternative names for languages.
    """
    __table_args__ = (UniqueConstraint('id', 'name', 'type'),)
    id = Column(String)
    type = Column(String)


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


class LanguageSource(Base, Versioned):
    language_pk = Column(Integer, ForeignKey('language.pk'))
    source_pk = Column(Integer, ForeignKey('source.pk'))
    source = relationship(
        Source,
        backref=backref("languagesource", cascade="all, delete-orphan"))
    language = relationship(
        Language,
        backref=backref("languagesource", cascade="all, delete-orphan"))


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
    contributor = relationship(Contributor, backref='contribution_assocs')


class ValueSentence(Base, PolymorphicBaseMixin, Versioned):
    """Many-to-many association between values and sentences given as explanation of a
    value.
    """
    value_pk = Column(Integer, ForeignKey('value.pk'))
    sentence_pk = Column(Integer, ForeignKey('sentence.pk'))
    description = Column(Unicode())

    value = relationship(Value, backref='sentence_assocs')
    sentence = relationship(Sentence, backref='value_assocs')


class UnitParameterUnit(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin):
    unit_pk = Column(Integer, ForeignKey('unit.pk'))
    unitparameter_pk = Column(Integer, ForeignKey('unitparameter.pk'))
    unit = relationship(Unit, backref='unitparameter_assocs')
    unitparameter = relationship(UnitParameter, backref='unit_assocs')
