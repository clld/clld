from __future__ import unicode_literals
import re
import unicodedata
import collections
import string

from six import PY3
from sqlalchemy.types import SchemaType, TypeDecorator, Enum


class NoDefault(object):
    pass

NO_DEFAULT = NoDefault()


#
# From "The Enum Recipe": http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
#
class EnumSymbol(object):
    """Define a fixed symbol tied to a parent class."""

    def __init__(self, cls_, name, value, description):
        self.cls_ = cls_
        self.name = name
        self.value = value
        self.description = description

    def __reduce__(self):
        """Allow unpickling to return the symbol linked to the DeclEnum class."""
        return getattr, (self.cls_, self.name)

    def __iter__(self):
        return iter([self.value, self.description])

    def __repr__(self):
        return "<%s>" % self.name


class EnumMeta(type):
    """Generate new DeclEnum classes."""

    def __init__(cls, classname, bases, dict_):
        cls._reg = reg = cls._reg.copy()
        for k, v in dict_.items():
            if isinstance(v, tuple):
                sym = reg[v[0]] = EnumSymbol(cls, k, *v)
                setattr(cls, k, sym)
        return type.__init__(cls, classname, bases, dict_)

    def __iter__(cls):
        return iter(cls._reg.values())


class DeclEnum(object):
    """Declarative enumeration."""

    __metaclass__ = EnumMeta
    _reg = {}

    @classmethod
    def from_string(cls, value):
        try:
            return cls._reg[value]
        except KeyError:
            raise ValueError("Invalid value for %r: %r" % (cls.__name__, value))

    @classmethod
    def values(cls):
        return cls._reg.keys()

    @classmethod
    def db_type(cls):
        return DeclEnumType(cls)


class DeclEnumType(SchemaType, TypeDecorator):
    def __init__(self, enum):
        self.enum = enum
        self.impl = Enum(
            *enum.values(),
            name="ck%s" % re.sub(
                '([A-Z])', lambda m: "_" + m.group(1).lower(), enum.__name__))

    def _set_table(self, table, column):
        self.impl._set_table(table, column)

    def copy(self):
        return DeclEnumType(self.enum)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum.from_string(value.strip())


class UnicodeMixin(object):
    def __unicode__(self):
        """
        :return: a human readable label for the object
        """
        return '%s' % self

    def __str__(self):
        """
        :return: a human readable label for the object, appropriately encoded (or not)
        """
        if PY3:
            return self.__unicode__()  # pragma: no cover
        return self.__unicode__().encode('utf-8')


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, parent_key=new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# Standard abbreviations according to the Leipzig Glossing Rules
# see http://www.eva.mpg.de/lingua/resources/glossing-rules.php
LGR_ABBRS = {
    'A': 'agent-like argument of canonical transitive verb',
    'ABL': 'ablative',
    'ABS': 'absolutive',
    'ACC': 'accusative',
    'ADJ': 'adjective',
    'ADV': 'adverb(ial)',
    'AGR': 'agreement',
    'ALL': 'allative',
    'ANTIP': 'antipassive',
    'APPL': 'applicative',
    'ART': 'article',
    'AUX': 'auxiliary',
    'BEN': 'benefactive',
    'CAUS': 'causative',
    'CLF': 'classifier',
    'COM': 'comitative',
    'COMP': 'complementizer',
    'COMPL': 'completive',
    'COND': 'conditional',
    'COP': 'copula',
    'CVB': 'converb',
    'DAT': 'dative',
    'DECL': 'declarative',
    'DEF': 'definite',
    'DEM': 'demonstrative',
    'DET': 'determiner',
    'DIST': 'distal',
    'DISTR': 'distributive',
    'DU': 'dual',
    'DUR': 'durative',
    'ERG': 'ergative',
    'EXCL': 'exclusive',
    'F': 'feminine',
    'FOC': 'focus',
    'FUT': 'future',
    'GEN': 'genitive',
    'IMP': 'imperative',
    'INCL': 'inclusive',
    'IND': 'indicative',
    'INDF': 'indefinite',
    'INF': 'infinitive',
    'INS': 'instrumental',
    'INTR': 'intransitive',
    'IPFV': 'imperfective',
    'IRR': 'irrealis',
    'LOC': 'locative',
    'M': 'masculine',
    'N': 'neuter',
    'N-': 'non- (e.g. NSG nonsingular, NPST nonpast)',
    'NEG': 'negation, negative',
    'NMLZ': 'nominalizer/nominalization',
    'NOM': 'nominative',
    'OBJ': 'object',
    'OBL': 'oblique',
    'P': 'patient-like argument of canonical transitive verb',
    'PASS': 'passive',
    'PFV': 'perfective',
    'PL': 'plural',
    'POSS': 'possessive',
    'PRED': 'predicative',
    'PRF': 'perfect',
    'PRS': 'present',
    'PROG': 'progressive',
    'PROH': 'prohibitive',
    'PROX': 'proximal/proximate',
    'PST': 'past',
    'PTCP': 'participle',
    'PURP': 'purposive',
    'Q': 'question particle/marker',
    'QUOT': 'quotative',
    'RECP': 'reciprocal',
    'REFL': 'reflexive',
    'REL': 'relative',
    'RES': 'resultative',
    'S': 'single argument of canonical intransitive verb',
    'SBJ': 'subject',
    'SBJV': 'subjunctive',
    'SG': 'singular',
    'TOP': 'topic',
    'TR': 'transitive',
    'VOC': 'vocative',
}


def slug(s):
    """
    :return: A condensed version of the string s, containing only lowercase alphanumeric \
    characters.
    """
    res = ''.join((c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn'))
    res = res.lower()
    for c in string.punctuation:
        res = res.replace(c, '')
    res = re.sub('\s+', '', res)
    res = res.encode('ascii', 'ignore').decode('ascii')
    assert re.match('[a-z0-9]*$', res)
    return res
