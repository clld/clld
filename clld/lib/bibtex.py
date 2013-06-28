"""
Functionality to handle bibligraphical data in the BibTeX format.

.. seealso:: http://en.wikipedia.org/wiki/BibTeX
"""
from collections import OrderedDict
import re

from clld.util import UnicodeMixin, DeclEnum
from clld.lib.bibutils import convert


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
    'address',  # Publisher's address (usually just the city, but can be the full address for lesser-known publishers)
    'annote',  # An annotation for annotated bibliography styles (not typical)
    'author',  # The name(s) of the author(s) (in the case of more than one author, separated by and)
    'booktitle',  # The title of the book, if only part of it is being cited
    'chapter',  # The chapter number
    'crossref',  # The key of the cross-referenced entry
    'edition',  # The edition of a book, long form (such as "First" or "Second")
    'editor',  # The name(s) of the editor(s)
    'eprint',  # A specification of an electronic publication, often a preprint or a technical report
    'howpublished',  # How it was published, if the publishing method is nonstandard
    'institution',  # The institution that was involved in the publishing, but not necessarily the publisher
    'journal',  # The journal or magazine the work was published in
    'key',  # A hidden field used for specifying or overriding the alphabetical order of entries (when the "author" and "editor" fields are missing). Note that this is very different from the key (mentioned just after this list) that is used to cite or cross-reference the entry.
    'month',  # The month of publication (or, if unpublished, the month of creation)
    'note',  # Miscellaneous extra information
    'number',  # The "(issue) number" of a journal, magazine, or tech-report, if applicable. (Most publications have a "volume", but no "number" field.)
    'organization',  # The conference sponsor
    'pages',  # Page numbers, separated either by commas or double-hyphens.
    'publisher',  # The publisher's name
    'school',  # The school where the thesis was written
    'series',  # The series of books the book was published in (e.g. "The Hardy Boys" or "Lecture Notes in Computer Science")
    'title',  # The title of the work
    'type',  # The field overriding the default type of publication (e.g. "Research Note" for techreport, "{PhD} dissertation" for phdthesis, "Section" for inbook/incollection)
    'url',  # The WWW address
    'volume',  # The volume of a journal or multi-volume book
    'year',
]


class Record(OrderedDict, UnicodeMixin):
    """A BibTeX record is basically an ordered dict with two special properties - id and
    genre.
    """
    def __init__(self, genre, id_, *args, **kwargs):
        self.genre = genre
        self.id = id_
        super(Record, self).__init__(args, **kwargs)

    @classmethod
    def from_object(cls, obj, **kw):
        data = dict()
        for field in FIELDS:
            value = getattr(obj, field, None)
            if value:
                data[field] = value
        data.update(kw)
        return cls(obj.bibtex_type, obj.id, **data)

    @classmethod
    def from_string(cls, bibtexString):
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
                        data[m.group('field')] = value[:-1].strip()
                else:
                    m = endLine.match(line)
                    if m:
                        break

        return cls(genre, id_, **data)

    def __unicode__(self):
        fields = []
        m = max([0] + list(map(len, self.keys())))

        for k in self.keys():
            values = self[k]
            if not isinstance(values, (tuple, list)):
                values = [values]
            fields.append(
                "  %s = {%s}," % (k.ljust(m), " and ".join(filter(None, values))))

        return """@%s{%s,
%s
}
""" % (getattr(self.genre, 'value', self.genre), self.id, "\n".join(fields)[:-1])

    def text(self):
        res = ["%s (%s)" % (self.get('author', 'Anonymous'), self.get('year', 's.a.'))]
        if self.get('title'):
            res.append('"%s"' % self.get('title', ''))
        if self.get('editor'):
            res.append("in %s (ed)" % self.get('editor'))
        if self.get('booktitle'):
            res.append("%s" % self.get('booktitle'))
        for attr in ['school', 'journal', 'volume']:
            if self.get(attr):
                res.append(self.get(attr))
        if self.get('issue'):
            res.append("(%s)" % self['issue'])
        if self.get('pages'):
            res[-1] += '.'
            res.append("pp. %s" % self['pages'])
        if self.get('publisher'):
            res[-1] += '.'
            res.append("%s: %s" % (self.get('address', ''), self['publisher']))
        res[-1] += '.'
        return ' '.join(res)

    def format(self, fmt):
        if fmt == 'txt':
            return self.text()
        if fmt == 'en':
            return convert(self.__unicode__(), 'bib', 'end')
        if fmt == 'ris':
            return convert(self.__unicode__(), 'bib', 'ris')
        if fmt == 'mods':
            return convert(self.__unicode__(), 'bib')
