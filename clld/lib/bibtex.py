# -*- coding: utf-8 -*-
"""
Functionality to handle bibligraphical data in the BibTeX format.

.. seealso:: http://en.wikipedia.org/wiki/BibTeX
"""
from collections import OrderedDict
import re
import codecs

from path import path
from zope.interface import Interface, implementer
from six import PY3

from clld.util import UnicodeMixin, DeclEnum
from clld.lib.bibutils import convert
from clld.lib import latex


latex.register()


if PY3:  # pragma: no cover
    unicode = str
    unichr = chr


UU_PATTERN = re.compile('\?\[\\\\u(?P<number>[0-9]{3,4})\]')


def u_unescape(s):
    """
    Unencode Unicode escape sequences
    match all 3/4-digit sequences with unicode character
    replace all '?[\u....]' with corresponding unicode

    There are some decimal/octal mismatches in unicode encodings in bibtex

    >>> r = u_unescape(r'?[\u123] ?[\u1234]')
    """
    new = []
    e = 0
    for m in UU_PATTERN.finditer(s):
        new.append(s[e:m.start()])
        e = m.end()

        digits = hex(int(m.group('number')))[2:].rjust(4, '0')
        r = False
        try:
            r = (u'\\u' + digits).decode('unicode_escape')
        except (UnicodeDecodeError, TypeError):  # pragma: no cover
            pass
        if r:
            new.append(r)
        else:
            new.append(s[m.start():m.end()])  # pragma: no cover
    new.append(s[e:len(s)])
    return ''.join(new)


RE_XML_ILLEGAL = re.compile(
    u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' +
    u'|' +
    u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' %
    (
        unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
        unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
        unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
    ))


def stripctrlchars(string):
    """remove unicode invalid characters

    >>> stripctrlchars(u'a\u0008\u000ba')
    u'aa'
    """
    try:
        return RE_XML_ILLEGAL.sub("", string)
    except TypeError:  # pragma: no cover
        return string


SYMBOLS = {
    r'\plusminus{}': u'\xb1',
    r'\middot{}': u'\xb7',
    r'\textopeno{}': u"\u0254",
    r'\dh{}': u"\u00f0",
    r'\DH{}': u"\u00d0",
    r'\textthorn{}': u"\u00fe",
    r'\textless{}': u"<",
    r'\textgreater{}': u">",
    r'\circ{}': u"\u00b0",
    r'\textltailn{}': u"\u0272",
    r'\textlambda{}': u"\u03BB",
    r'\textepsilon{}': u'\u025b',
    r'\textquestiondown{}': u'\xbf',
    r'\textschwa{}': u'\u0259',
    r'\textsubdot{o}': u'\u1ecd',
    r'\textrhooktopd{}': u'\u0257',
    #r'\eurosign{}': u'\u20ac',
    r'\eurosign{}': u'\u2021',
    r'\textquestiondown': u'\xbf',
    r'\textquotedblleft': u'\u201c',
    r'\textquotedblright': u'\u201d',
    r'\textquoteleft': u'\u2018',
    r'\textquoteright': u'\u2019',

    r'\textsubdot{D}': u'\u1e0c',
    r'\textsubdot{E}': u'\u1eb8',
    r'\textsubdot{H}': u'\u1e24',
    r'\textsubdot{I}': u'\u1eca',
    r'\textsubdot{O}': u'\u1ecc',
    r'\textsubdot{T}': u'\u1e6c',
    r'\textsubdot{d}': u'\u1e0d',
    r'\textsubdot{b}': u'\u1e05',
    r'\textsubdot{e}': u'\u1eb9',
    r'\textsubdot{h}': u'\u1e25',
    r'\textsubdot{i}': u'\u1ecb',
    r'\textsubdot{n}': u'\u1e47',
    r'\textsubdot{r}': u'\u1e5b',
    r'\textsubdot{s}': u'\u1e63',
    r'\textsubdot{t}': u'\u1e6d',
    r'\ng{}': u'\u014b',
    r'\oslash{}': u'\u00f8',
    r'\Oslash{}': u'\u00d8',
    r'\textdoublebarpipe{}': u'\u01c2',
    #r'\dots': '',
    r'\Aa{}': u'\xc5',
    u'\\Aa{}Rsj\xd6': u'\xc5rsj\xf6',

    r'\guillemotleft': u'\xab',
    r'\guillemotleft{}': u'\xab',
    r'\guillemotright': u'\xbb',
}


def unescape(string):
    """transform latex escape sequences of type \`\ae  into unicode
    """
    def _delatex(s):
        try:
            t = str(s)
            result = t.decode('latex+latin1')
        except UnicodeEncodeError:  # pragma: no cover
            result = string
        u_result = unicode(result)
        return u_result

    res = u_unescape(_delatex(stripctrlchars(unicode(string).strip())))
    for symbol in sorted(SYMBOLS.keys(), key=lambda s: len(s)):
        res = res.replace(symbol, SYMBOLS[symbol])
    if '\\' not in res:
        res = res.replace('{', '')
        res = res.replace('}', '')
    return res


class EntryType(DeclEnum):
    """
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
    A part of a book, usually untitled. May be a chapter (or section or whatever) and/or
    a range of pages.
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
    Optional fields: editor, volume/number, series, pages, address, month, organization,
    publisher, note, key
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
    A report published by a school or other institution, usually numbered within a series.
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


class _Convertable(UnicodeMixin):
    """Mixin adding a shortcut to clld.lib.bibutils.convert as method.
    """
    def format(self, fmt):
        if fmt == 'txt':
            if hasattr(self, 'text'):
                return self.text()
            raise NotImplementedError()  # pragma: no cover
        if fmt == 'en':
            return convert(self.__unicode__(), 'bib', 'end')
        if fmt == 'ris':
            return convert(self.__unicode__(), 'bib', 'ris')
        if fmt == 'mods':
            return convert(self.__unicode__(), 'bib')
        return self.__unicode__()


class IRecord(Interface):
    """marker
    """


@implementer(IRecord)
class Record(OrderedDict, _Convertable):
    """A BibTeX record is basically an ordered dict with two special properties - id and
    genre.

    To overcome the limitation of single values per field in BibTeX, we allow fields,
    i.e. values of the dict to be iterables of strings as well.
    Note that to support this use case comprehensively, various methods of retrieving
    values will behave differently. I.e. values will be

    - joined to a string in __getitem__,
    - retrievable as assigned with get (i.e. only use get if you know how a value was\
      assigned),
    - retrievable as list with getall

    .. note:: Unknown genres are converted to "misc".

    >>> r = Record('article', '1', author=['a', 'b'], editor='a and b')
    >>> assert r['author'] == 'a and b'
    >>> assert r.get('author') == r.getall('author')
    >>> assert r['editor'] == r.get('editor')
    >>> assert r.getall('editor') == ['a', 'b']
    """
    def __init__(self, genre, id_, *args, **kw):
        if isinstance(genre, basestring):
            try:
                genre = EntryType.from_string(genre.lower())
            except ValueError:
                genre = EntryType.misc
        self.genre = genre
        self.id = id_
        super(Record, self).__init__(args, **kw)

    @classmethod
    def from_object(cls, obj, **kw):
        data = dict()
        for field in FIELDS:
            value = getattr(obj, field, None)
            if value:
                data[field] = value
        data.update(kw)
        data.setdefault('title', obj.description)
        rec = cls(obj.bibtex_type, obj.id)
        for key in sorted(data.keys()):
            rec[key] = data[key]
        return rec

    @classmethod
    def from_string(cls, bibtexString, lowercase=False):
        id_, genre, data = None, None, {}

        # the following patterns are designed to match preprocessed input lines.
        # i.e. the configuration values given in the bibtool resource file used to
        # generate the bib-file have to correspond to these patterns.

        # in particular, we assume all key-value-pairs to fit on one line,
        # because we don't want to deal with nested curly braces!
        lines = bibtexString.strip().split('\n')

        # genre and key are parsed from the @-line:
        atLine = re.compile("^@(?P<genre>[a-zA-Z_]+)\s*{\s*(?P<key>[^,]*)\s*,\s*")

        # since all key-value pairs fit on one line, it's easy to determine the
        # end of the value: right before the last closing brace!
        fieldLine = re.compile('\s*(?P<field>[a-zA-Z_]+)\s*=\s*(\{|")(?P<value>.+)')

        endLine = re.compile("}\s*")

        # flag to signal, whether the @-line - starting each bibtex record - was
        # already encountered:
        inRecord = False

        while lines:
            line = lines.pop(0)
            if not inRecord:
                m = atLine.match(line)
                if m:
                    id_ = m.group('key').strip()
                    genre = m.group('genre').strip().lower()
                    inRecord = True
            else:
                m = fieldLine.match(line)
                if m:
                    value = m.group('value').strip()
                    if value.endswith(','):
                        value = value[:-1].strip()
                    if value.endswith('}') or value.endswith('"'):
                        field = m.group('field')
                        if lowercase:
                            field = field.lower()
                        data[field] = value[:-1].strip()
                else:
                    m = endLine.match(line)
                    if m:
                        break
                    # Note: fields with names not matching the expected pattern are simply
                    # ignored.

        return cls(genre, id_, **data)

    @staticmethod
    def sep(key):
        return ' and ' if key in ['author', 'editor'] else '; '

    def getall(self, key):
        """
        :return: list of strings representing the values of the record for field 'key'.
        """
        res = self.get(key, [])
        if isinstance(res, basestring):
            res = res.split(Record.sep(key))
        return filter(None, res)

    def __getitem__(self, key):
        """
        :return: string representing the concatenation of the values for field 'key'.
        """
        value = OrderedDict.__getitem__(self, key)
        if not isinstance(value, (tuple, list)):
            value = [value]
        return Record.sep(key).join(filter(None, value))

    def __unicode__(self):
        """
        :return: string encoding the record in BibTeX syntax.
        """
        fields = []
        m = max([0] + list(map(len, self.keys())))

        for k in self.keys():
            fields.append("  %s = {%s}," % (k.ljust(m), self[k]))

        return """@%s{%s,
%s
}
""" % (getattr(self.genre, 'value', self.genre), self.id, "\n".join(fields)[:-1])

    def text(self):
        """linearize the bib record according to the rules of the unified style

        Book:
        author. year. booktitle. (series, volume.) address: publisher.

        Article:
        author. year. title. journal volume(issue). pages.

        Incollection:
        author. year. title. In editor (ed.), booktitle, pages. address: publisher.

        .. seealso::

            http://celxj.org/downloads/UnifiedStyleSheet.pdf
            https://github.com/citation-style-language/styles/blob/master/\
            unified-style-linguistics.csl
        """
        genre = getattr(self.genre, 'value', self.genre)
        if self.get('editor'):
            editors = self['editor']
            affix = 'eds' if ' and ' in editors or '&' in editors else 'ed'
            editors = " %s (%s.)" % (editors, affix)
        else:
            editors = None

        res = [self.get('author', editors), self.get('year', 'n.d')]
        if genre == 'book':
            res.append(self.get('booktitle') or self.get('title'))
            res.append(', '.join(filter(None, [self.get('series'), self.get('volume')])))
        elif genre == 'misc':
            # in case of misc records, we use the note field in case a title is missing.
            res.append(self.get('title') or self.get('note'))
        else:
            res.append(self.get('title'))

        if genre == 'article':
            atom = ' '.join(filter(None, [self.get('journal'), self.get('volume')]))
            if self.get('issue'):
                atom += '(%s)' % self['issue']
            res.append(atom)
            res.append(self.get('pages'))
        elif genre == 'incollection':
            prefix = 'In'
            atom = ''
            if editors:
                atom += editors
            if self.get('booktitle'):
                if atom:
                    atom += ','
                atom += " %s" % self['booktitle']
            if self.get('pages'):
                atom += ", %s" % self['pages']
            res.append(prefix + atom)
        else:
            # check for author to make sure we haven't included the editors yet.
            if editors and self.get('author'):
                res.append("In %s" % editors)

            for attr in ['school', 'journal', 'volume']:
                if self.get(attr):
                    res.append(self.get(attr))

            if self.get('issue'):
                res.append("(%s)" % self['issue'])

            if self.get('pages'):
                res.append(self['pages'])

        if self.get('publisher'):
            res.append(": ".join(filter(None, [self.get('address'), self['publisher']])))

        note = self.get('note')
        if note and note not in res:
            res.append('(%s)' % note)

        return ' '.join(
            map(lambda a: a + ('' if a.endswith('.') else '.'), filter(None, res)))


class IDatabase(Interface):
    """marker
    """


@implementer(IDatabase)
class Database(_Convertable):
    """
    a class to handle bibtex databases, i.e. a container class for Record instances.
    """
    def __init__(self, records):
        self.records = filter(lambda r: r.genre and r.id, records)
        self._keymap = None

    def __unicode__(self):
        return '\n'.join(r.__unicode__() for r in self.records)

    @property
    def keymap(self):
        """map bibtex record ids to list index
        """
        if self._keymap is None:
            self._keymap = dict((r.id, i) for i, r in enumerate(self.records))
        return self._keymap

    @classmethod
    def from_file(cls, bibFile, encoding='utf8', lowercase=False):
        """
        a bibtex database defined by a bib-file

        @param bibFile: path of the bibtex-database-file to be read.
        """
        if path(bibFile).exists():
            with codecs.open(bibFile, encoding=encoding) as fp:
                content = fp.read()
        else:
            content = ''

        return cls([Record.from_string('@' + r, lowercase=lowercase)
                    for r in content.split('@')[1:]])

    def __len__(self):
        return len(self.records)

    def __getitem__(self, key):
        """to access bib records by index or citation key"""
        return self.records[key if isinstance(key, int) else self.keymap[key]]

    def __iter__(self):
        return iter(self.records)
