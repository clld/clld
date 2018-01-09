# coding: utf8
"""Functionality to create Coins, i.e. context objects in spans.

.. seealso:: http://ocoins.info/
"""
from __future__ import unicode_literals
import re

from six import string_types, binary_type
from six.moves.urllib.parse import urlencode

from clldutils.misc import UnicodeMixin, encoded, to_binary


FIELDS = {
    'any': {
        'rft_id': None,
        'aulast': None,  # First author's family name. This may be more than one word.
        # In many citations, the author's family name is recorded first and is followed
        # by a comma, i.e. Smith, Fred James is recorded as "aulast=smith"
        'aufirst': None,  # First author's given name or names or initials. This data
        # element may contain multiple words and punctuation, i.e. "Fred F", "Fred James"
        'auinit': None,  # First author's first and middle initials.
        'auinit1': None,  # First author's first initial.
        'auinitm': None,  # First author's middle initial.
        'ausuffix': None,  # First author's name suffix. Qualifiers on an author's name
        # such as "Jr.", "III" are entered here. i.e. Smith, Fred Jr. is recorded as
        # "ausuffux=jr"
        'au': None,  # This data element contains the full name of a single author, i. e.
        # "Smith, Fred M", "Harry S. Truman". (au is repeatable)
        'aucorp': None,  # Organization or corporation that is the author or creator of
        # the book, i.e. "Mellon Foundation"
        'title': None,  # Book title. Provided for compatibility with version 0.1.
        # Prefer btitle.
        'place': None,  # Place of publication. "New York"
        'pub': None,  # Publisher name. "Harper and Row"
        'date': None,  # Date of publication. Book dates are assumed to be a single year.
    },
    'dissertation': {
        'inst': None,
        'degree': None,
    },
    'book': {
        'btitle': None,  # The title of the book. This can also be expressed as title, for
        # compatibility with version 0.1. "moby dick or the white whale"
        'isbn': None,  # International Standard Book Number (ISBN). The ISBN is usually
        # presented as 9 digits plus a final check digit (which may be "X"), i.e.
        # "057117678X" but it may contain hyphens, i.e. "1-878067-73-7"
        'atitle': None,  # Chapter title. Chapter title is included if it is a distinct
        # title, i.e. "The Push Westward."
        'edition': None,  # Statement of the edition of the book. This will usually be a
        # phrase, with or without numbers, but may be a single number. I.e.
        # "First edition", "4th ed."
        'tpages': None,  # Total pages. Total pages is the largest recorded number of
        # pages, if this can be determined. I.e., "ix, 392 p." would be recorded as "392"
        # in tpages. This data element is usually available only for monographs (books and
        # printed reports). In some cases, tpages may not be numeric, i.e. "F36"
        'series': None,  # The title of a series in which the book or document was issued.
        # There may also be an ISSN associated with the series.
        'spage': None,  # First page number of a start/end (spage-epage) pair.
        # Note that pages are not always numeric.
        'epage': None,  # Second (ending) page number of a start/end (spage-epage) pair.
        'pages': None,  # Start and end pages for parts of a book, i.e. "124-147". This
        # can also be used for an unstructured pagination statement when data relating to
        # pagination cannot be interpreted as a start-end pair, i.e. "A7, C4-9", "1-3,6".
        # This data element includes the OpenURL 0.1 definition of "pages".
        'issn': None,  # International Standard Serials Number (ISSN). The issn may
        # contain a hyphen, i.e. "1041-5653". An ISSN in the book format is often
        # associated with a series title.
        'genre': lambda val: val if val in [
            'book',  # a publication that is complete in one part or a designated finite
            # number of parts, often identified with an ISBN.
            'bookitem',  # a defined section of a book, usually with a separate title or
            # number.
            'proceeding',  # a conference paper or proceeding published in a conference
            # publication.
            'conference',  # a publication bundling the proceedings of a conference.
            'report',  # report or technical report is a published document that is
            # issued by an organization, agency or government body.
            'document',  # general document type to be used when available data elements
            # do not allow determination of a more specific document type, i.e. when one
            # has only author and title but no publication information.
            'unknown',  # use when the genre of the document is unknown.
        ] else None,
    },
    'journal': {
        'rft_id': None,
        'atitle': None,  # Article title.
        'jtitle': None,  # Journal title. Use the most complete title available.
        # Abbreviated titles, when known, are records in stitle. This can also be
        # expressed as title, for compatibility with version 0.1. "journal of the
        # american medical association"
        'stitle': None,  # Abbreviated or short journal title. This is used for journal
        # title abbreviations, where known, i.e. "J Am Med Assn"
        'volume': None,  # Volume designation.Volume is usually expressed as a number but
        # could be roman numerals or non-numeric, i.e. "124", or "VI".
        'issue': None,  # This is the designation of the published issue of a journal,
        # corresponding to the actual physical piece in most cases. While usually numeric,
        # it could be non-numeric. Note that some publications use chronology in the place
        # of enumeration, i.e. Spring, 1998.
        'spage': None,  # First page number of a start/end (spage-epage) pair. Note that
        # pages are not always numeric.
        'epage': None,  # Second (ending) page number of a start/end (spage-epage) pair.
        'pages': None,  # Start and end pages, i.e. "53-58". This can also be used for an
        # unstructured pagination statement when data relating to pagination cannot be
        # interpreted as a start-end pair, i.e. "A7, C4-9", "1-3,6". This data element
        # includes the OpenURL 0.1 definition of "pages".
        'artnum': None,  # Article number assigned by the publisher. Article numbers are
        # often generated for publications that do not have usable pagination, in
        # particular electronic journal articles, i.e. "unifi000000090". A URL may be the
        # only usable identifier for an online article, in which case the URL can be
        # treated as an identifier for the article (i.e.
        # "rft_id=http://www.firstmonday.org/ issues/issue6_2/odlyzko/ index.html").
        'issn': None,  # International Standard Serials Number (ISSN). The issn may
        # contain a hyphen, i.e. "1041-5653"
        'eissn': None,  # ISSN for electronic version of the journal. Although there is no
        # distinction by format in the assignment of ISSNs, some bibliographic services
        # now carry both the ISSN for the paper version and a separate ISSN for the
        # electronic version. This data element is included here to allow the OpenURL to
        # carry both ISSNs and distinguish them.
        'isbn': None,  # International Standard Book Number (ISBN). The ISBN is usually
        # presented as 9 digits plus a final check digit (which may be "X"), i.e.
        # "057117678X" but it may contain hyphens, i.e. "1-878067-73-7"
        'coden': None,  # CODEN
        'sici': None,  # Serial Item and Contribution Identifier (SICI)
        'genre': lambda val: val if val in [
            'issue',  # one instance of the serial publication.
            'article',  # a document published in a journal.
            'proceeding',  # a single conference presentation published in a journal or
            # serial publication
            'conference',  # a record of a conference that includes one or more conference
            # papers and that is published as an issue of a journal or serial publication
            'preprint',  # an individual paper or report published in paper or
            # electronically prior to its publication in a journal or serial.
            'unknown',  # use when the genre of the document is unknown.
        ] else None,
        'chron': None,  # Enumeration or chronology in not-normalized form, i.e.
        # "1st quarter". Where numeric dates are also available, place the numeric portion
        # in the "date" Key. So a recorded date of publication of "1st quarter 1992"
        # becomes date=1992&chron=1st quarter. Normalized indications of chronology can be
        # provided in the ssn and quarter Keys.
        'ssn': lambda val: val if val in ['spring', 'summer', 'fall', 'winter'] else None,
        # Season (chronology). Legitimate values are spring, summer, fall, winter
        'quarter': lambda val: val if int(val) in [1, 2, 3, 4] else None,
        # Quarter (chronology).
        'part': None,  # Part can be a special subdivision of a volume or it can be the
        # highest level division of the journal. Parts are often designated with letters
        # or names, i.e. "B", "Supplement".
    },
}


def _encoded(value):
    if not isinstance(value, binary_type) and not isinstance(value, string_types):
        value = '%s' % value
    return encoded(value)


class ContextObject(list, UnicodeMixin):

    """A Context Object which knows how to render it's metadata as HTML span tags."""

    def __init__(self, sid, mtx, *data):
        self.sid = sid
        self.mtx = mtx
        list.__init__(self)
        for key, val in data:
            validator = FIELDS[self.mtx].get(key, FIELDS['any'].get(key)) or _encoded
            key = 'rft.' + key if not key.startswith('rft') else key
            self.append((key, validator(val)))

    @classmethod
    def from_bibtex(cls, sid, rec):
        mtx, genre = {
            'article': ('journal', 'article'),
            'book': ('book', 'book'),
            'inbook': ('book', 'bookitem'),
            'incollection': ('book', 'bookitem'),
            'inproceedings': ('book', 'proceeding'),
            'conference': ('book', 'proceeding'),
            'mastersthesis': ('dissertation', None),
            'phdthesis': ('dissertation', None),
            'proceedings': ('book', 'conference'),
            'techreport': ('book', 'report'),
            'unpublished': ('book', 'document'),
            'misc': ('book', 'unknown'),
        }.get(getattr(rec.genre, 'value', rec.genre),  # allow EnumSymbol as genre.
              ('book', 'document' if rec.get('author') else 'unknown'))
        if genre:
            data = [('genre', genre)]
        else:
            data = []

        if mtx == 'journal':
            if 'title' in rec:
                data.append(('atitle', rec['title']))
            if 'journal' in rec:
                data.append(('jtitle', rec['journal']))
        elif mtx == 'book':
            if 'title' in rec:
                data.append(('btitle' if genre == 'book' else 'atitle', rec['title']))
            if 'booktitle' in rec:
                if genre != 'book':
                    data.append(('btitle', rec['booktitle']))
        elif mtx == 'dissertation':
            if 'title' in rec:
                data.append(('title', rec['title']))
            data.append(
                ('degree', 'phd' if
                 getattr(rec.genre, 'value', rec.genre) == 'phdthesis' else 'masters'))
            data.append(('inst', rec.get('school', rec.get('institution', ''))))

        if 'url' in rec:
            data.append(('rft_id', rec['url']))

        for bibfield, openurlfield in {
            'address': 'place',
            'publisher': 'pub',
            'year': 'date',
            'volume': 'volume',
            'number': 'issue',
            'series': 'series',
            'edition': 'edition',
            'pages': 'pages',
        }.items():
            if bibfield in rec:
                data.append((openurlfield, rec[bibfield]))

        for i, author in enumerate(rec.getall('author')):
            if i == 0:
                parts = re.split('\s*,\s*', author, 1)
                if len(parts) == 1:
                    parts = re.split('\s+', author)
                    last = parts[-1]
                    first = ' '.join(parts[:-1])
                else:
                    last, first = parts
                data.append(('aulast', last))
                data.append(('aufirst', first))
            else:
                data.append(('au', author))

        return cls(sid, mtx, *data)

    def __unicode__(self):
        pairs = [
            (to_binary('ctx_ver'), to_binary('Z39.88-2004')),
            (to_binary('rft_val_fmt'),
             to_binary('info:ofi/fmt:kev:mtx:') + _encoded(self.mtx)),
            (to_binary('rfr_id'), to_binary('info:sid/') + _encoded(self.sid))]
        for pair in self:
            pairs.append((_encoded(pair[0]), _encoded(pair[1])))
        try:
            return urlencode(pairs)
        except UnicodeDecodeError:  # pragma: no cover
            return to_binary('')

    def span_attrs(self):
        return {'class': 'Z3988', 'title': self.__unicode__()}
