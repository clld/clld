"""Generic utility functions."""
from __future__ import unicode_literals, print_function, division, absolute_import
import re
import unicodedata
import string
from datetime import date, datetime
import json

from six import PY3, string_types, text_type, add_metaclass, binary_type
from sqlalchemy.types import SchemaType, TypeDecorator, Enum
import dateutil.parser


DATETIME_ISO_FORMAT = re.compile(
    '[0-9]{4}\-[0-9]{2}\-[0-9]{2}T[0-9]{2}\:[0-9]{2}\:[0-9]{2}\.[0-9]+')


def parse_json_with_datetime(d):
    """
    convert iso formatted timestamps found as values in the dict d to datetime objects.

    :return: A shallow copy of d with converted timestamps.
    """
    res = {}
    for k, v in d.items():
        if isinstance(v, string_types) and DATETIME_ISO_FORMAT.match(v):
            v = dateutil.parser.parse(v)
        res[k] = v
    return res


def format_json(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def jsondump(obj, path, **kw):
    """python 2 + 3 compatible version of json.dump.

    :param obj: The object to be dumped.
    :param path: The path of the JSON file to be written.
    """
    _kw = dict(mode='w')
    if PY3:  # pragma: no cover
        _kw['encoding'] = 'utf8'
    with open(path, **_kw) as fp:
        return json.dump(obj, fp, **kw)


def jsonload(path, **kw):
    """python 2 + 3 compatible version of json.load.

    :return: The python object read from path.
    """
    _kw = {}
    if PY3:  # pragma: no cover
        _kw['encoding'] = 'utf8'
    with open(path, **_kw) as fp:
        return json.load(fp, **kw)


def nfilter(seq):
    """Replacement for python 2's filter(None, seq).

    :return: a list filtered from seq containing only truthy items.
    """
    return [e for e in seq if e]


def to_binary(s, encoding='utf8'):
    """Portable cast function.

    In python 2 the ``str`` function which is used to coerce objects to bytes does not
    accept an encoding argument, whereas python 3's ``bytes`` function requires one.

    :param s: object to be converted to binary_type
    :return: binary_type instance, representing s.
    """
    if PY3:  # pragma: no cover
        return s if isinstance(s, binary_type) else binary_type(s, encoding=encoding)
    return binary_type(s)


def dict_merged(d, _filter=None, **kw):
    """Update dictionary d with the items passed as kw if the value passes _filter."""
    if not _filter:
        _filter = lambda s: s is not None
    d = d or {}
    for k, v in kw.items():
        if _filter(v):
            d[k] = v
    return d


class NoDefault(object):
    def __repr__(self):
        return '<NoDefault>'


#: A singleton which can be used to distinguish no-argument-passed from None passed as
#: argument in callables with optional arguments.
NO_DEFAULT = NoDefault()


def xmlchars(text):
    """Not all of UTF-8 is considered valid character data in XML ...

    Thus, this function can be used to remove illegal characters from ``text``.
    """
    invalid = list(range(0x9))
    invalid.extend([0xb, 0xc])
    invalid.extend(range(0xe, 0x20))
    return re.sub('|'.join('\\x%0.2X' % i for i in invalid), '', text)


def format_size(num):
    """Format byte-sizes.

    .. seealso:: http://stackoverflow.com/a/1094933
    """
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


class UnicodeMixin(object):

    """Portable label mixin."""

    def __unicode__(self):
        """a human readable label for the object."""
        return '%s' % self  # pragma: no cover

    if PY3:  # pragma: no cover
        def __str__(self):
            """a human readable label for the object, appropriately encoded (or not)."""
            return self.__unicode__()
    else:
        def __str__(self):
            """a human readable label for the object, appropriately encoded (or not)."""
            return self.__unicode__().encode('utf-8')


#
# From "The Enum Recipe": http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
#
class EnumSymbol(UnicodeMixin):

    """Define a fixed symbol tied to a parent class."""

    def __init__(self, cls_, name, value, description, *args):
        self.cls_ = cls_
        self.name = name
        self.value = value
        self.description = description
        self.args = args

    def __reduce__(self):
        """Allow unpickling to return the symbol linked to the DeclEnum class."""
        return getattr, (self.cls_, self.name)  # pragma: no cover

    def __iter__(self):
        return iter([self.value, self.description])

    def __repr__(self):
        return "<%s>" % self.name

    def __unicode__(self):
        return self.value

    def __lt__(self, other):
        return self.value < getattr(other, 'value', None)

    def __json__(self, request=None):
        return self.value


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
        return iter(sorted(cls._reg.values()))


@add_metaclass(EnumMeta)
class DeclEnum(object):

    """Declarative enumeration."""

    _reg = {}

    @classmethod
    def from_string(cls, value):
        try:
            return cls._reg[value]
        except KeyError:
            raise ValueError("Invalid value for %r: %r" % (cls.__name__, value))

    @classmethod
    def values(cls):
        return list(cls._reg.keys())

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
        self.impl._set_table(table, column)  # pragma: no cover

    def copy(self):
        return DeclEnumType(self.enum)  # pragma: no cover

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum.from_string(value.strip())


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


def slug(s, remove_whitespace=True, lowercase=True):
    """Condensed version of s, containing only lowercase alphanumeric characters."""
    res = ''.join((c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn'))
    if lowercase:
        res = res.lower()
    for c in string.punctuation:
        res = res.replace(c, '')
    res = re.sub('\s+', '' if remove_whitespace else ' ', res)
    res = res.encode('ascii', 'ignore').decode('ascii')
    assert re.match('[ A-Za-z0-9]*$', res)
    return res


def encoded(string, encoding='utf8'):
    """Cast string to binary_type.

    :param string: six.binary_type or six.text_type
    :param encoding: encoding which the object is forced to
    :return: six.binary_type
    """
    assert isinstance(string, string_types) or isinstance(string, binary_type)
    if isinstance(string, text_type):
        return string.encode(encoding)
    try:
        # make sure the string can be decoded in the specified encoding ...
        string.decode(encoding)
        return string
    except UnicodeDecodeError:
        # ... if not use latin1 as best guess to decode the string before encoding as
        # specified.
        return string.decode('latin1').encode(encoding)


class cached_property(object):

    """Decorator for read-only properties evaluated only once.

    It can be used to create a cached property like this::

        import random

        # the class containing the property must be a new-style class
        class MyClass(object):
            # create property whose value is cached
            @cached_property()
            def randint(self):
                # will only be evaluated once.
                return random.randint(0, 100)

    The value is cached  in the '_cache' attribute of the object instance that
    has the property getter method wrapped by this decorator. The '_cache'
    attribute value is a dictionary which has a key for every property of the
    object which is wrapped by this decorator. Each entry in the cache is
    created only when the property is accessed for the first time and is the last
    computed property value.

    To expire a cached property value manually just do::

        del instance._cache[<property name>]

    inspired by the recipe by Christopher Arndt in the PythonDecoratorLibrary
    """

    def __call__(self, fget):
        self.fget = fget
        self.__doc__ = fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst, owner):
        if not hasattr(inst, '_cache'):
            inst._cache = {}
        if self.__name__ not in inst._cache:
            inst._cache[self.__name__] = self.fget(inst)
        return inst._cache[self.__name__]
