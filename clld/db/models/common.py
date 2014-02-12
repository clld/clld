"""
Common models for all clld apps
"""
from __future__ import unicode_literals
import os
from collections import OrderedDict
from datetime import date
from itertools import product, groupby

from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    Boolean,
    Unicode,
    Date,
    CheckConstraint,
    UniqueConstraint,
    ForeignKey,
    desc,
)
from sqlalchemy.orm import (
    relationship,
    validates,
    backref,
    joinedload_all,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin, DBSession
from clld.db.versioned import Versioned
from clld import interfaces
from clld.util import DeclEnum, cached_property
from clld.lib import bibtex
from clld.lib import coins
from clld.web.util.htmllib import HTML
from clld.web.icon import ORDERED_ICONS


class Config(Base):
    """Model class to allow storage of key-value pairs of configuration data in the
    database. This model is also (ab-)used to implement a mechanism linking database
    objects of all types without enforcing referential intagrity, e.g. to model chains
    of superseding objects, where referred objects may become obsolete themselves.
    """
    key = Column(Unicode)
    value = Column(Unicode)

    gone = '__gone__'

    @staticmethod
    def replacement_key(model, id_):
        """
        :param model: Model class or instance.
        :param id_: Identifier of a class instance.
        :return: ``str`` representation identifying a database object.
        """
        mapper_name = model if isinstance(model, basestring) else model.mapper_name()
        return '__%s_%s__' % (mapper_name, id_)

    @classmethod
    def get_replacement_id(cls, model, id_):
        """
        :return: id of a resource registered as replacement for the specified resource.
        """
        res = DBSession.query(cls.value)\
            .filter(cls.key == cls.replacement_key(model, id_)).first()
        if res:
            return res[0]

    @classmethod
    def add_replacement(cls, replaced, replacement, model=None, session=None):
        """Method to register a replacement relation.

        :param replaced: db object or identifier of the object to be replaced.
        :param replacement: db object or identifier of the superseding object.
        :param model: If only an identifier is passed as ``replaced`` or ``replacement``\
        the corresponding model class must be passed as ``model``.
        :param session: Db session the relation is added to.
        """
        session = session or DBSession
        value = getattr(replacement, 'id', replacement) if replacement else cls.gone
        session.add(cls(
            key=cls.replacement_key(model or replaced, getattr(replaced, 'id', replaced)),
            value=value))


class IdNameDescriptionMixin(object):
    """Mixin for 'visible' objects, i.e. anything that has to be displayed (to humans or
    machines); in particular all :doc:`resources` fall into this category.

    .. note::

        Only one of :py:attr:`clld.db.models.common.IdNameDescriptionMixin.description`
        or :py:attr:`clld.db.models.common.IdNameDescriptionMixin.markup_description`
        should be supplied, since these are used mutually exclusively.
    """
    #: A ``str`` identifier of an object which can be used for sorting and as part of a
    #: URL path; thus should be limited to characters valid in URLs, and should not
    #: contain '.' or '/' since this may trip up route matching.
    id = Column(String, unique=True)

    #: A human readable 'identifier' of the object.
    name = Column(Unicode)

    #: A description of the object.
    description = Column(Unicode)

    #: A description of the object containing HTML markup.
    markup_description = Column(Unicode)


#-----------------------------------------------------------------------------
# We augment mapper classes for basic objects using mixins to add the ability
# to store arbitrary key-value pairs and files associated with an object.
#-----------------------------------------------------------------------------
class FilesMixin(IdNameDescriptionMixin):
    """This mixin provides a way to associate files with instances of another model class.

    .. note::

        The file itself is not stored in the database but must be created in the
        filesystem, e.g. using the create method.
    """
    @classmethod
    def owner_class(cls):
        return cls.__name__.split('_')[0]

    #: Ordinal to control sorting of files associated with one db object.
    ord = Column(Integer, default=1)

    #: Mime-type of the file content.
    mime_type = Column(String)

    @declared_attr
    def object_pk(cls):
        return Column(Integer, ForeignKey('%s.pk' % cls.owner_class().lower()))

    @property
    def relpath(self):
        """OS file path of the file relative to the application's file-system directory.
        """
        return os.path.join(self.owner_class().lower(), str(self.object.id), str(self.id))

    def create(self, dir_, content):
        """Write ``content`` to a file using ``dir_`` as file-system directory.

        :return: File-system path of the file that was created.
        """
        p = dir_.joinpath(self.relpath)
        p.dirname().makedirs_p()
        with open(p, 'wb') as fp:
            fp.write(content)
        return p


class HasFilesMixin(object):
    """Mixin for model classes which may have associated files.
    """
    @property
    def files(self):
        """
        :return: ``dict`` of associated files keyed by ``id``.
        """
        return dict((f.id, f) for f in self._files)

    @declared_attr
    def _files(cls):
        return relationship(cls.__name__ + '_files', backref='object')


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

        It is the responsibility of the programmer to make sure conversion to a ``dict``
        makes sense, i.e. the keys in data are actually unique, thus usable as dictionary
        keys.
    """
    def datadict(self):
        """
        :return: ``dict`` of associated key-value pairs.
        """
        return dict((d.key, d.value) for d in self.data)

    @declared_attr
    def data(cls):
        return relationship(cls.__name__ + '_data', order_by=cls.__name__ + '_data.ord')


class LanguageSource(Base, Versioned):
    __table_args__ = (UniqueConstraint('language_pk', 'source_pk'),)
    language_pk = Column(Integer, ForeignKey('language.pk'))
    source_pk = Column(Integer, ForeignKey('source.pk'))


def _add_solr_language_info(res, obj):
    """
    :param res: Solr document, i.e. a dict to which new keys will be added.
    :param obj: object which is searched for language information.
    :return: mutated dict res
    """
    if getattr(obj, 'language', None):
        res['language_t'] = obj.language.name
        obj = obj.language

    for attr in ['iso_code', 'glottocode']:
        value = getattr(obj, attr, None)
        if value:
            res.update({attr + '_s': value})
    return res


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
    publisher_name = Column(Unicode)
    publisher_place = Column(Unicode)
    publisher_url = Column(String)
    license = Column(String, default="http://creativecommons.org/licenses/by/3.0/")
    domain = Column(String, nullable=False)
    contact = Column(String)

    def get_stats(self, resources, **filters):
        """
        :param resources:
        :param filters:
        :return:
        """
        res = OrderedDict()
        for rsc in resources:
            if rsc.name != 'combination':
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

    def __solr__(self, req):
        res = Base.__solr__(self, req)
        res['altname_txt'] = [i.name for i in self.identifiers if i.type == 'name']
        return _add_solr_language_info(res, self)


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


class CombinationDomainElement(object):
    def __init__(self, combination, domainelements, icon=None):
        self.number = tuple(de.number for de in domainelements)
        self.id = '-'.join(map(str, self.number))
        self.name = ' / '.join(de.name for de in domainelements)
        self.icon = icon
        self.languages = []


@implementer(interfaces.ICombination)
class Combination(object):
    """A combination of parameters
    """
    delimiter = '_'

    def __init__(self, *parameters):
        """
        :param parameters: distinct Parameter instances.
        """
        assert len(parameters) < 5
        assert len(set(parameters)) == len(parameters)
        self.id = self.delimiter.join(map(str, [p.id for p in parameters]))
        self.name = ' / '.join(p.name for p in parameters)
        self.parameters = parameters
        # we keep track of languages with multiple values.
        self.multiple = []

    @classmethod
    def mapper_name(cls):
        return str('combination')

    @classmethod
    def get(cls, id_, **kw):
        params = []
        for pid in set(id_.split(cls.delimiter)):
            params.append(
                DBSession.query(Parameter)
                .filter(Parameter.id == pid)
                .options(joinedload_all(Parameter.domain))
                .one())
        return cls(*params)

    @cached_property()
    def domain(self):
        """
        .. note::

            This does only work well with parameters which have a discrete domain.
        """
        d = OrderedDict()
        for i, des in enumerate(product(*[p.domain for p in self.parameters])):
            cde = CombinationDomainElement(
                self, des, icon=ORDERED_ICONS[i % len(ORDERED_ICONS)])
            d[cde.number] = cde

        for language, values in groupby(
            sorted(self.values, key=lambda v: v.valueset.language_pk),
            lambda i: i.valueset.language,
        ):
            # values may contain multiple values for the same parameter, so we have to
            # group those, too.
            values_by_parameter = OrderedDict()
            for p in self.parameters:
                values_by_parameter[p.pk] = []
            for v in values:
                values_by_parameter[v.valueset.parameter_pk].append(v)
            for i, cv in enumerate(product(*values_by_parameter.values())):
                d[tuple(v.domainelement.number for v in cv)].languages.append(language)
                if i > 0:
                    # a language with multiple values, store a reference.
                    self.multiple.append(language)
        self.multiple = set(self.multiple)
        return d.values()

    @cached_property()
    def values(self):
        def _filter(query, operation):
            q = query.filter(Parameter.pk == self.parameters[0].pk)
            return getattr(q, operation)(
                *[query.filter(Parameter.pk == p.pk) for p in self.parameters[1:]])

        # determine relevant languages, i.e. languages having a value for all parameters:
        languages = _filter(
            DBSession.query(Language.pk).join(ValueSet).join(Parameter),
            'intersect').subquery()

        # value query:
        return _filter(
            DBSession.query(Value)
            .join(Value.valueset)
            .join(ValueSet.parameter)
            .filter(ValueSet.language_pk.in_(languages))
            .options(
                joinedload_all(Value.domainelement),
                joinedload_all(Value.valueset, ValueSet.language)),
            'union').all()


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

    def __bibtex__(self):
        return {}

    def bibtex(self):
        exclude = ['gbs', 'glottolog_ref_id']
        kw = {k: self.jsondatadict[k] for k in self.jsondatadict if not k in exclude}
        kw.update(self.__bibtex__())
        return bibtex.Record.from_object(self, **kw)

    def coins(self, req):
        return HTML.span(
            ' ',
            **coins.ContextObject.from_bibtex(
                req.dataset.name, self.bibtex()).span_attrs()
        )


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

    def formatted_contributors(self):
        contribs = [' and '.join(c.name for c in self.primary_contributors)]
        if self.secondary_contributors:
            contribs.append(' and '.join(c.name for c in self.secondary_contributors))
        return ' with '.join(contribs)


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

    @declared_attr
    def contribution(cls):
        return relationship(
            'Contribution', backref=backref('valuesets', order_by=cls.parameter_pk))

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
    #: Inherited from IdNameDescriptionMixin:
    #: name: The text of the sentence in object language
    #: description: A translation of the sentence
    analyzed = Column(Unicode)
    gloss = Column(Unicode)
    type = Column(Unicode)
    source = Column(Unicode)
    comment = Column(Unicode)
    original_script = Column(Unicode)
    xhtml = Column(Unicode)

    #: The following columns store data which contains markup and should be looked at
    #: first, when rendering a sentence:
    markup_text = Column(Unicode)
    markup_analyzed = Column(Unicode)
    markup_gloss = Column(Unicode)
    markup_comment = Column(Unicode)

    language_pk = Column(Integer, ForeignKey('language.pk'))

    @declared_attr
    def language(cls):
        return relationship(
            'Language', backref=backref('sentences', order_by=cls.language_pk))

    def __solr__(self, req):
        return _add_solr_language_info(Base.__solr__(self, req), self)

    @property
    def audio(self):
        for f in self._files:
            if f.mime_type.split('/')[0] == 'audio':
                return f


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

    def __solr__(self, req):
        return _add_solr_language_info(Base.__solr__(self, req), self)


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
    iso = 'iso639-3', 'ISO 639-3', \
          'http://www.sil.org/iso639-3/documentation.asp?id={0.name}'
    wals = 'wals', 'WALS Code', 'http://wals.info/languoid/lect/wals_code_{0.name}'
    glottolog = 'glottolog', 'Glottocode', \
                'http://glottolog.org/resource/languoid/id/{0.name}'
    ethnologue = 'ethnologue', 'Ethnologue', 'http://www.ethnologue.com/language/{0.name}'


class Identifier(Base, Versioned, IdNameDescriptionMixin):
    """We want to be able to link languages to languages in other systems. Thus,
    we store identifiers of various types like 'wals', 'iso639-3', 'glottolog'.
    But we might as well just store alternative names for languages.
    """
    __table_args__ = (UniqueConstraint('name', 'type', 'description'),)
    id = Column(String)
    type = Column(String)
    lang = Column(String(3), default='en')

    def url(self):
        try:
            return IdentifierType.from_string(self.type).args[0].format(self)
        except ValueError:
            return


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


#
# TODO: UnitValueSentence!
#
class UnitParameterUnit(Base, PolymorphicBaseMixin, Versioned, IdNameDescriptionMixin):
    unit_pk = Column(Integer, ForeignKey('unit.pk'))
    unitparameter_pk = Column(Integer, ForeignKey('unitparameter.pk'))
    unit = relationship(Unit, backref='unitparameter_assocs')
    unitparameter = relationship(UnitParameter, backref='unit_assocs')
