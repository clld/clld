"""
Functionality to handle bibligraphical data in the BibTeX format.

.. seealso:: http://en.wikipedia.org/wiki/BibTeX
"""
import re
import pathlib
import collections

from zope.interface import Interface, implementer
from six import unichr, text_type, string_types, iteritems
from six.moves import filter
from clldutils.misc import to_binary
from clldutils.source import Source

from clld.util import DeclEnum
from clld.lib.bibutils import convert
from clld.lib import latex

__all__ = [
    'u_unescape', 'unescape', 'stripctrlchars',
    'EntryType', 'FIELDS', 'IRecord', 'Record', 'IDatabase', 'Database']

latex.register()

UU_PATTERN = re.compile(r'\?\[\\u(?P<number>[0-9]{3,5})\]')


def u_unescape(s):
    """Unencode Unicode escape sequences.

    Match all 3-5-digit sequences with unicode character
    replace all '?[\\u....]' with corresponding unicode

    There are some decimal/octal mismatches in unicode encodings in bibtex
    """
    def iterchunks(s):
        end = 0
        for m in UU_PATTERN.finditer(s):
            yield s[end:m.start()]
            yield unichr(int(m.group('number')))
            end = m.end()
        yield s[end:]

    return ''.join(iterchunks(s))


SYMBOLS = {
    '\\plusminus{}': '\xb1',
    '\\middot{}': '\xb7',
    '\\textopeno{}': "\u0254",
    '\\dh{}': "\u00f0",
    '\\DH{}': "\u00d0",
    '\\textthorn{}': "\u00fe",
    '\\textless{}': "<",
    '\\textgreater{}': ">",
    '\\circ{}': "\u00b0",
    '\\textltailn{}': "\u0272",
    '\\textlambda{}': "\u03BB",
    '\\textepsilon{}': '\u025b',
    '\\textquestiondown{}': '\xbf',
    '\\textschwa{}': '\u0259',
    '\\textsubdot{o}': '\u1ecd',
    '\\textrhooktopd{}': '\u0257',
    # '\\eurosign{}': '\u20ac',
    '\\eurosign{}': '\u2021',
    '\\textquestiondown': '\xbf',
    '\\textquotedblleft': '\u201c',
    '\\textquotedblright': '\u201d',
    '\\textquoteleft': '\u2018',
    '\\textquoteright': '\u2019',

    '\\textsubdot{D}': '\u1e0c',
    '\\textsubdot{E}': '\u1eb8',
    '\\textsubdot{H}': '\u1e24',
    '\\textsubdot{I}': '\u1eca',
    '\\textsubdot{O}': '\u1ecc',
    '\\textsubdot{T}': '\u1e6c',
    '\\textsubdot{d}': '\u1e0d',
    '\\textsubdot{b}': '\u1e05',
    '\\textsubdot{e}': '\u1eb9',
    '\\textsubdot{h}': '\u1e25',
    '\\textsubdot{i}': '\u1ecb',
    '\\textsubdot{n}': '\u1e47',
    '\\textsubdot{r}': '\u1e5b',
    '\\textsubdot{s}': '\u1e63',
    '\\textsubdot{t}': '\u1e6d',
    '\\ng{}': '\u014b',
    '\\oslash{}': '\u00f8',
    '\\Oslash{}': '\u00d8',
    '\\textdoublebarpipe{}': '\u01c2',
    # '\\dots': '',
    '\\Aa{}': '\xc5',
    '\\Aa{}Rsj\xd6': '\xc5rsj\xf6',

    '\\guillemotleft': '\xab',
    '\\guillemotleft{}': '\xab',
    '\\guillemotright': '\xbb',
}

RE_XML_ILLEGAL = re.compile(
    r'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])'
    + r'|'
    + r'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' %
    (
        unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
        unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
        unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
    ))


def stripctrlchars(string):
    try:
        return RE_XML_ILLEGAL.sub("", string)
    except TypeError:
        return string


def unescape(string):
    r"""Transform latex escape sequences of type \`\ae  into unicode.

    :param string: str or binary

    :return: str
    """
    def _delatex(s):
        try:
            t = to_binary(s, encoding='latin1')
            result = t.decode('latex+latin1')
        except UnicodeEncodeError:
            result = string
        u_result = text_type(result)
        return u_result

    res = u_unescape(stripctrlchars(_delatex(string.strip())))
    for symbol in sorted(SYMBOLS.keys(), key=lambda s: len(s)):
        res = res.replace(symbol, SYMBOLS[symbol])
    if '\\' not in res:
        res = res.replace('{', '')
        res = res.replace('}', '')
    return res


class EntryType(DeclEnum):

    """Bibtext entry types.

    article
        An article from a journal or magazine.
        Required fields: author, title, journal, year
        Optional fields: volume, number, pages, month, note, key

    book
        A book with an explicit publisher.
        Required fields: author/editor, title, publisher, year
        Optional fields: volume/number, series, address, edition, month, note, key

    booklet
        A work that is printed and bound, but without a named publisher or sponsoring
        institution.
        Required fields: title
        Optional fields: author, howpublished, address, month, year, note, key

    conference
        The same as inproceedings, included for Scribe compatibility.

    inbook
        A part of a book, usually untitled. May be a chapter (or section or whatever)
        and/or a range of pages.
        Required fields: author/editor, title, chapter/pages, publisher, year
        Optional fields: volume/number, series, type, address, edition, month, note, key

    incollection
        A part of a book having its own title.
        Required fields: author, title, booktitle, publisher, year
        Optional fields: editor, volume/number, series, type, chapter, pages, address,
        edition, month, note, key

    inproceedings
        An article in a conference proceedings.
        Required fields: author, title, booktitle, year
        Optional fields: editor, volume/number, series, pages, address, month,
        organization, publisher, note, key

    manual
        Technical documentation.
        Required fields: title
        Optional fields: author, organization, address, edition, month, year, note, key

    mastersthesis
        A Master's thesis.
        Required fields: author, title, school, year
        Optional fields: type, address, month, note, key

    misc
        For use when nothing else fits.
        Required fields: none
        Optional fields: author, title, howpublished, month, year, note, key

    phdthesis
        A Ph.D. thesis.
        Required fields: author, title, school, year
        Optional fields: type, address, month, note, key

    proceedings
        The proceedings of a conference.
        Required fields: title, year
        Optional fields: editor, volume/number, series, address, month, publisher,
        organization, note, key

    techreport
        A report published by a school or other institution, usually numbered within a
        series.
        Required fields: author, title, institution, year
        Optional fields: type, number, address, month, note, key

    unpublished
        A document having an author and title, but not formally published.
        Required fields: author, title, note
        Optional fields: month, year, key
    """

    article = 'article', 'article'  # Article
    book = 'book', 'book'  # Book
    booklet = 'booklet', 'booklet'
    conference = 'conference', 'conference'  # Conference
    inbook = 'inbook', 'inbook'  # BookSection
    incollection = 'incollection', 'incollection'
    inproceedings = 'inproceedings', 'inproceedings'
    manual = 'manual', 'manual'  # Manual
    mastersthesis = 'mastersthesis', 'mastersthesis'  # Thesis
    misc = 'misc', 'misc'
    phdthesis = 'phdthesis', 'phdthesis'  # Thesis
    proceedings = 'proceedings', 'proceedings'  # Proceedings
    techreport = 'techreport', 'techreport'  # Report
    unpublished = 'unpublished', 'unpublished'  # Manuscript


FIELDS = [
    'address',  # Publisher's address
    'annote',  # An annotation for annotated bibliography styles (not typical)
    'author',  # The name(s) of the author(s) (separated by and)
    'booktitle',  # The title of the book, if only part of it is being cited
    'chapter',  # The chapter number
    'crossref',  # The key of the cross-referenced entry
    'edition',  # The edition of a book, long form (such as "First" or "Second")
    'editor',  # The name(s) of the editor(s)
    'eprint',  # A specification of electronic publication, preprint or technical report
    'howpublished',  # How it was published, if the publishing method is nonstandard
    'institution',  # institution involved in the publishing,not necessarily the publisher
    'journal',  # The journal or magazine the work was published in
    'key',  # A hidden field used for specifying or overriding the orderalphabetical order
    'month',  # The month of publication (or, if unpublished, the month of creation)
    'note',  # Miscellaneous extra information
    'number',  # The "(issue) number" of a journal, magazine, or tech-report
    'organization',  # The conference sponsor
    'pages',  # Page numbers, separated either by commas or double-hyphens.
    'publisher',  # The publisher's name
    'school',  # The school where the thesis was written
    'series',  # The series of books the book was published in
    'title',  # The title of the work
    'type',  # The field overriding the default type of publication
    'url',  # The WWW address
    'volume',  # The volume of a journal or multi-volume book
    'year',
]

FIELDS_SET = set(FIELDS)


class _Convertable(object):

    """Mixin adding a shortcut to clld.lib.bibutils.convert as method."""

    def format(self, fmt):
        if fmt == 'txt':
            if hasattr(self, 'text'):
                return self.text()
            raise NotImplementedError('no text method found!')
        if fmt == 'en':
            return convert(str(self), 'bib', 'end')
        if fmt == 'ris':
            return convert(str(self), 'bib', 'ris')
        if fmt == 'mods':
            return convert(str(self), 'bib')
        return str(self)


class IRecord(Interface):

    """marker."""


@implementer(IRecord)
class Record(Source, _Convertable):

    """A BibTeX record is an ordered dict with two special properties - id and genre.

    To overcome the limitation of single values per field in BibTeX, we allow fields,
    i.e. values of the dict to be iterables of strings as well.
    Note that to support this use case comprehensively, various methods of retrieving
    values will behave differently. I.e. values will be

    - joined to a string in __getitem__,
    - retrievable as assigned with get (i.e. only use get if you know how a value was\
      assigned),
    - retrievable as list with getall

    .. note:: Unknown genres are converted to "misc".
    """

    def __init__(self, genre, id_, *args, **kw):
        super(Record, self).__init__(genre, 'a', args, **kw)
        self.id = id_
        if isinstance(self.genre, string_types):
            try:
                self.genre = EntryType.from_string(genre.lower())
            except ValueError:
                self.genre = EntryType.misc

    @classmethod
    def from_object(cls, obj, **kw):
        data = {}
        for field in FIELDS:
            value = getattr(obj, field, None)
            if value:
                data[field] = value
        data.update(kw)
        data.setdefault('title', obj.description)
        data = sorted(iteritems(data))
        return cls(obj.bibtex_type, obj.id, *data)

    @classmethod
    def from_string(cls, bibtexString, lowercase=False):
        return cls.from_bibtex(bibtexString, lowercase=lowercase)

    @staticmethod
    def sep(key):
        return ' and ' if key in ('author', 'editor') else '; '

    def getall(self, key):
        """Get list of all values for key.

        :return: list of strings representing the values of the record for field 'key'.
        """
        res = self.get(key, [])
        if isinstance(res, string_types):
            res = res.split(Record.sep(key))
        return [_f for _f in res if _f]

    def __getitem__(self, key):
        """Get concatenated string of all values for key.

        :return: string representing the concatenation of the values for field 'key'.
        """
        value = collections.OrderedDict.__getitem__(self, key)
        if not isinstance(value, (tuple, list)):
            value = [value]
        return Record.sep(key).join(filter(None, value))

    def __str__(self):
        """Represent the record in BibTeX format.

        :return: string encoding the record in BibTeX syntax.
        """
        keys = sorted(self, key=lambda k: (k not in FIELDS_SET, k))
        m = max([0] + list(map(len, keys)))

        fields = ("  %s = {%s}" % (k.ljust(m), self[k]) for k in keys)

        return "@%s{%s,\n%s\n}" % (
            getattr(self.genre, 'value', self.genre), self.id, ",\n".join(fields))


class IDatabase(Interface):

    """marker."""


@implementer(IDatabase)
class Database(_Convertable):

    """Represents a bibtex databases, i.e. a container class for Record instances."""

    def __init__(self, records):
        self.records = [r for r in records if r and r.genre and r.id]
        self._keymap = None

    def __str__(self):
        return '\n'.join(str(r) for r in self.records)

    @property
    def keymap(self):
        """Map bibtex record ids to list index."""
        if self._keymap is None:
            self._keymap = dict((r.id, i) for i, r in enumerate(self.records))
        return self._keymap

    @classmethod
    def from_file(cls, bibFile, encoding='utf8', lowercase=False):
        """Create bibtex database from a bib-file.

        @param bibFile: path of the bibtex-database-file to be read.
        """
        bibFile = pathlib.Path(bibFile)
        content = bibFile.read_text(encoding=encoding) if bibFile.exists() else ''

        return cls((Record.from_string('@' + m, lowercase=lowercase)
                    for m in re.split(r'^\s*@', content, 0, re.MULTILINE)))

    def __len__(self):
        return len(self.records)

    def __getitem__(self, key):
        """Access bib records by index or citation key."""
        return self.records[key if isinstance(key, int) else self.keymap[key]]

    def __iter__(self):
        return iter(self.records)
