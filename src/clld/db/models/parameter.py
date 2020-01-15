import itertools
import collections

from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, joinedload

from zope.interface import implementer
from clldutils.misc import lazyproperty

from clld.db.meta import Base, PolymorphicBaseMixin, DBSession
from clld import interfaces
from clld.web.icon import ORDERED_ICONS

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin,
    Language)

__all__ = ('DomainElement', 'Parameter', 'Combination')


class DomainElement_data(Base, DataMixin):
    pass


class DomainElement_files(Base, FilesMixin):
    pass


@implementer(interfaces.IDomainElement)
class DomainElement(Base,
                    PolymorphicBaseMixin,
                    IdNameDescriptionMixin,
                    HasDataMixin,
                    HasFilesMixin):

    """DomainElements can be used to model controlled lists of values for a Parameter."""

    __table_args__ = (
        UniqueConstraint('parameter_pk', 'name'),
        UniqueConstraint('parameter_pk', 'number'),
    )

    parameter_pk = Column(Integer, ForeignKey('parameter.pk'), nullable=False)

    number = Column(Integer, doc='numerical value of the domain element')
    """the number is used to sort domain elements within the domain of one parameter"""

    abbr = Column(Unicode, doc='abbreviated name')
    """abbreviated name, e.g. as label for map legends"""

    def url(self, request):
        return request.resource_url(self.parameter, _anchor='DE-' + self.id)


class Parameter_data(Base, DataMixin):
    pass


class Parameter_files(Base, FilesMixin):
    pass


@implementer(interfaces.IParameter)
class Parameter(Base,
                PolymorphicBaseMixin,
                IdNameDescriptionMixin,
                HasDataMixin,
                HasFilesMixin):

    """A measurable attribute of a language."""

    __table_args__ = (UniqueConstraint('name'),)

    domain = relationship(
        'DomainElement', backref='parameter', order_by=DomainElement.number)


class CombinationDomainElement(object):
    def __init__(self, combination, domainelements, icon=None):
        self.number = tuple(de.number for de in domainelements)
        self.id = '-'.join(str(n) for n in self.number)
        self.name = ' / '.join(de.name for de in domainelements)
        self.icon = icon
        self.languages = []
        super(CombinationDomainElement, self).__init__()


@implementer(interfaces.ICombination)
class Combination(object):

    """A combination of parameters."""

    delimiter = '_'

    def __init__(self, *parameters):
        """Initialize.

        :param parameters: distinct Parameter instances.
        """
        assert len(parameters) < 5
        assert len(set(parameters)) == len(parameters)
        self.id = self.delimiter.join(str(p.id) for p in parameters)
        self.name = ' / '.join(p.name for p in parameters)
        self.parameters = parameters
        # we keep track of languages with multiple values.
        self.multiple = []
        super(Combination, self).__init__()

    def __json__(self, *args, **kw):
        return {k: getattr(self, k) for k in ['id', 'name']}

    @classmethod
    def get(cls, id_, **kw):
        params = []
        for pid in set(id_.split(cls.delimiter)):
            params.append(
                DBSession.query(Parameter)
                .filter(Parameter.id == pid)
                .options(joinedload(Parameter.domain))
                .one())
        return cls(*params)

    @lazyproperty
    def domain(self):
        """Compute the domain as cartesian product of constituent domains.

        .. note::

            This does only work well with parameters which have a discrete domain.
        """
        d = collections.OrderedDict()
        for i, des in enumerate(itertools.product(*[p.domain for p in self.parameters])):
            cde = CombinationDomainElement(
                self, des, icon=ORDERED_ICONS[i % len(ORDERED_ICONS)])
            d[cde.number] = cde

        for language, values in itertools.groupby(
            sorted(self.values, key=lambda v: v.valueset.language_pk),
            lambda i: i.valueset.language,
        ):
            # values may contain multiple values for the same parameter, so we have to
            # group those, too.
            values_by_parameter = collections.OrderedDict()
            for p in self.parameters:
                values_by_parameter[p.pk] = []
            for v in values:
                values_by_parameter[v.valueset.parameter_pk].append(v)
            for i, cv in enumerate(itertools.product(*values_by_parameter.values())):
                d[tuple(v.domainelement.number for v in cv)].languages.append(language)
                if i > 0:
                    # a language with multiple values, store a reference.
                    self.multiple.append(language)
        self.multiple = set(self.multiple)
        return list(d.values())

    @lazyproperty
    def values(self):
        from . import ValueSet, Value

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
                joinedload(Value.domainelement),
                joinedload(Value.valueset).joinedload(ValueSet.language)),
            'union').all()
