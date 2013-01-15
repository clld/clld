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


class File(Base):
    """Model for storage of files in the database.
    """
    name = Column(Unicode)
    mime_type = Column(String)
    content = Column(LargeBinary)


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

    @declared_attr
    def object(cls):
        return relationship(cls.owner_class(), backref=backref('data', order_by=cls.ord))


class HasDataMixin(object):
    """Adds a convenience method to retrieve the key-value pairs from data as dict.

    .. note::

        It is the responsibility of the programmer to make sure conversion to a dict makes
        sense, i.e. the keys in data are actually unique.
    """
    def datadict(self):
        return dict((d.key, d.value) for d in self.data)


class IdNameDescriptionMixin(object):
    """id is to be used as string identifier which can be used for sorting and as
    URL part.
    """
    id = Column(String, unique=True)
    name = Column(Unicode)
    description = Column(Unicode)


class Language_data(Base, Versioned, DataMixin):
    pass


@implementer(interfaces.ILanguage)
class Language(Base,
               PolymorphicBaseMixin,
               Versioned,
               IdNameDescriptionMixin,
               HasDataMixin):
    """Languages are the main objects of discourse. We attach a geo-coordinate
    to them to be able to put them on maps.
    """
    __table_args__ = (UniqueConstraint('name'),)
    latitude = Column(Float(), CheckConstraint('-90 <= latitude and latitude <= 90'))
    longitude = Column(Float(), CheckConstraint('-180 <= longitude and longitude <= 180 '))
    identifiers = association_proxy('languageidentifier', 'identifier')


class Identifier(Base, Versioned, IdNameDescriptionMixin):
    """We want to be able to link languages to languages in other systems. Thus,
    we store identifiers of various types like 'wals', 'iso_639_3', 'glottolog'.
    """
    __table_args__ = (UniqueConstraint('name', 'type'), UniqueConstraint('id'))
    type = Column(String)

    def url(self):
        """
        :return: canonical URL for a language identifier
        """
        #
        # TODO!
        #
        if self.type == 'wals':
            return 'http://wals.info/...'


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


@implementer(interfaces.IDomainElement)
class DomainElement(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin):
    __table_args__ = (UniqueConstraint('name', 'parameter_pk'),)

    parameter_pk = Column(Integer, ForeignKey('parameter.pk'))

    # do we need a numeric value for these?


@implementer(interfaces.IParameter)
class Parameter(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin):
    __table_args__ = (UniqueConstraint('name'),)
    domain = relationship('DomainElement', backref='parameter', order_by=DomainElement.id)


class Source_data(Base, DataMixin, Versioned):
    pass


@implementer(interfaces.ISource)
class Source(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin, HasDataMixin):
    glottolog_id = Column(String)
    google_book_search_id = Column(String)


@implementer(interfaces.IContribution)
class Contribution(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin):  # TODO: hasData, hasFiles
    __table_args__ = (UniqueConstraint('name'),)
    date = Column(Date)

    @property
    def primary_contributors(self):
        return [assoc.contributor for assoc in
                sorted(self.contributor_assocs, key=lambda a: a.ord) if assoc.primary]

    @property
    def secondary_contributors(self):
        return [assoc.contributor for assoc in
                sorted(self.contributor_assocs, key=lambda a: a.ord) if not assoc.primary]


@implementer(interfaces.IValue)
class Value(Base, PolymorphicBaseMixin, Versioned):
    id = Column(Integer, unique=True)
    language_pk = Column(Integer, ForeignKey('language.pk'))
    parameter_pk = Column(Integer, ForeignKey('parameter.pk'))
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    description = Column(Unicode())

    # Values may be taken from a domain.
    domainelement_pk = Column(Integer, ForeignKey('domainelement.pk'))

    # Languages may have multiple values for the same parameter. Their relative
    # frequency can be stored here.
    frequency = Column(Float)

    parameter = relationship('Parameter', backref='values')
    domainelement = relationship('DomainElement', backref='values')
    contribution = relationship('Contribution', backref='values')

    @declared_attr
    def language(cls):
        return relationship('Language', backref=backref('values', order_by=cls.language_pk))

    #
    # TODO: examples
    #

    @validates('parameter_pk')
    def validate_parameter_pk(self, key, parameter_pk):
        """We have to make sure, the parameter a value is tied to and the parameter a
        possible domainelement is tied to stay in sync.
        """
        if self.domainelement:
            assert self.domainelement.parameter_pk == parameter_pk
        return parameter_pk


class Reference(Base, Versioned):
    """Values (or Examples?) are linked to Sources with an optional description of this
    linkage, e.g. 'pp. 30-34'.
    """
    key = Column(Unicode)  # the citation key, specific (and unique) within a contribution
    value_pk = Column(Integer, ForeignKey('value.pk'))
    source_pk = Column(Integer, ForeignKey('source.pk'))

    # since examples are linked to values, isn't it sufficient to store the references for
    # examples as references of the value? Not if value-example is many-to-many!
    #example_pk = Column(Integer, ForeignKey('example.pk'))

    description = Column(Unicode)

    source = relationship(Source, backref='references')

    @declared_attr
    def value(cls):
        return relationship(Value, backref=backref("references", order_by=cls.key))


@implementer(interfaces.IContributor)
class Contributor(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin):
    __table_args__ = (UniqueConstraint('name'),)
    url = Column(Unicode())
    email = Column(String)
    address = Column(Unicode)


@implementer(interfaces.IExample)
class Example(Base, PolymorphicBaseMixin, Versioned):
    pass


class ContributionContributor(Base, PolymorphicBaseMixin, Versioned):
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contributor_pk = Column(Integer, ForeignKey('contributor.pk'))
    ord = Column(Integer, default=1)
    primary = Column(Boolean, default=True)
    contribution = relationship(Contribution, backref='contributor_assocs')
    contributor = relationship(Contributor, backref='contribution_assocs')


class ValueExample(Base, PolymorphicBaseMixin, Versioned):
    value_pk = Column(Integer, ForeignKey('value.pk'))
    example_pk = Column(Integer, ForeignKey('example.pk'))
    description = Column(Unicode())


class ExampleReference(Base, PolymorphicBaseMixin, Versioned):
    example_pk = Column(Integer, ForeignKey('example.pk'))
    reference_pk = Column(Integer, ForeignKey('reference.pk'))
    description = Column(Unicode())  # pages, accessed on, ...


class Unit_data(Base, DataMixin, Versioned):
    pass


@implementer(interfaces.IUnit)
class Unit(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin, HasDataMixin):
    pass
    # link to language


@implementer(interfaces.IUnitParameter)
class UnitParameter(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin):
    pass


class UnitParameterUnit(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin):
    unit_pk = Column(Integer, ForeignKey('unit.pk'))
    unitparameter_pk = Column(Integer, ForeignKey('unitparameter.pk'))
    unit = relationship(Unit, backref='unitparameter_assocs')
    unitparameter = relationship(UnitParameter, backref='unit_assocs')
