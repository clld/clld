from collections import OrderedDict

from clld.util import UnicodeMixin

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


class Record(OrderedDict, UnicodeMixin):

    def __init__(self, genre, id, *args, **kwargs):
        self.genre = genre
        self.id = id
        super(Record, self).__init__(args, **kwargs)

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
""" % (self.genre, self.id, "\n".join(fields)[:-1])

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
