# coding: utf8
"""Support for reading delimiter-separated value files.

This module contains unicode aware replacements for :func:`csv.reader`
and :func:`csv.writer`.  It was stolen/extracted from the ``csvkit``
project to allow re-use when the whole ``csvkit`` package isn't
required.

The original implementations were largely copied from
`examples in the csv module documentation <http://docs.python.org/library/csv.html\
#examples>`_.

.. seealso:: http://en.wikipedia.org/wiki/Delimiter-separated_values
"""
from __future__ import unicode_literals, division, absolute_import, print_function
import codecs
import csv
from collections import namedtuple
import keyword
from string import ascii_letters

from six import (
    string_types, text_type, PY3, PY2, Iterator, binary_type, BytesIO, StringIO,
)
from path import path

from clld.util import slug, to_binary, encoded


class UTF8Recoder(object):

    """Iterator that reads an encoded stream and reencodes the input to UTF-8."""

    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')


class UnicodeWriter(object):

    """Write Unicode data to a csv file."""

    def __init__(self, f=None, encoding='utf8', **kw):
        self.f = f
        self.encoding = encoding
        self.kw = kw
        self._close = False

    def __enter__(self):
        if isinstance(self.f, string_types) or isinstance(self.f, path):
            if PY3:  # pragma: no cover
                self.f = open(self.f, 'wt', encoding=self.encoding, newline='')
            else:
                self.f = open(self.f, 'wb')
            self._close = True
        elif self.f is None:
            self.f = StringIO(newline='') if PY3 else BytesIO()

        self.writer = csv.writer(self.f, **self.kw)
        return self

    def read(self):
        if hasattr(self.f, 'seek'):
            self.f.seek(0)
        if hasattr(self.f, 'read'):
            res = self.f.read()
            if PY3:  # pragma: no cover
                res = res.encode('utf8')
            return res

    def __exit__(self, type, value, traceback):
        if self._close:
            self.f.close()

    def writerow(self, row):
        if not PY3:
            row = ['' if s is None else encoded('%s' % s, self.encoding) for s in row]
        self.writer.writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UnicodeReader(Iterator):

    """Read Unicode data from a csv file."""

    def __init__(self, f, **kw):
        self.f = f
        self.encoding = kw.pop('encoding', 'utf8')
        self.newline = kw.pop('lineterminator', None)
        self.kw = kw
        self._close = False

    def __enter__(self):
        if isinstance(self.f, string_types) or isinstance(self.f, path):
            if PY3:  # pragma: no cover
                self.f = open(
                    self.f, 'rt', encoding=self.encoding, newline=self.newline or '')
            else:
                self.f = open(self.f, 'rU')
            self._close = True
        elif hasattr(self.f, 'read'):
            if PY2:
                self.f = UTF8Recoder(self.f, self.encoding)
        else:
            lines = []
            for line in self.f:
                if PY2 and isinstance(line, text_type):
                    line = line.encode(self.encoding)
                elif PY3 and isinstance(line, binary_type):  # pragma: no cover
                    line = line.decode(self.encoding)
                lines.append(line)
            self.f = lines
        self.reader = csv.reader(self.f, **self.kw)
        return self

    def __next__(self):
        row = next(self.reader)
        return [s if isinstance(s, text_type) else s.decode(self.encoding) for s in row]

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._close:
            self.f.close()

    def __iter__(self):
        return self


class UnicodeDictReader(UnicodeReader):

    """Read Unicode data represented as one dictionary per row."""

    def __init__(self, f, fieldnames=None, restkey=None, restval=None, **kw):
        self._fieldnames = fieldnames   # list of keys for the dict
        self.restkey = restkey          # key to catch long rows
        self.restval = restval          # default value for short rows
        self.line_num = 0
        UnicodeReader.__init__(self, f, **kw)

    @property
    def fieldnames(self):
        if self._fieldnames is None:
            try:
                self._fieldnames = UnicodeReader.__next__(self)
            except StopIteration:
                pass
        self.line_num = self.reader.line_num
        return self._fieldnames

    def __next__(self):
        if self.line_num == 0:
            # Used only for its side effect.
            self.fieldnames
        row = UnicodeReader.__next__(self)
        self.line_num = self.reader.line_num

        # unlike the basic reader, we prefer not to return blanks,
        # because we will typically wind up with a dict full of None
        # values
        while row == []:
            row = UnicodeReader.__next__(self)
        return self.item(row)

    def item(self, row):
        d = dict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d


class NamedTupleReader(UnicodeDictReader):

    """Read namedtuple objects from a csv file."""

    def __init__(self, f, **kw):
        self._cls = None
        UnicodeDictReader.__init__(self, f, **kw)

    @property
    def cls(self):
        if self._cls is None:
            self._cls = namedtuple('Row', list(map(normalize_name, self.fieldnames)))
        return self._cls

    def item(self, row):
        d = UnicodeDictReader.item(self, row)
        for name in self.fieldnames:
            d.setdefault(name, None)
        return self.cls(
            **{normalize_name(k): v for k, v in d.items() if k in self.fieldnames})


def normalize_name(s):
    """Convert a string into a valid python attribute name.

    This function is called to convert ASCII strings to something that can pass as
    python attribute name, to be used with namedtuples.
    """
    s = s.replace('-', '_').replace('.', '_').replace(' ', '_')
    if s in keyword.kwlist:
        return s + '_'
    s = '_'.join(slug(ss, lowercase=False) for ss in s.split('_'))
    if not s:
        s = '_'
    if s[0] not in ascii_letters + '_':
        s = '_' + s
    return s


def reader(lines_or_file, namedtuples=False, dicts=False, encoding='utf8', **kw):
    """Convenience factory function for csv reader.

    :param lines_or_file: Content to be read. Either a file handle, a file path or a list\
    of strings.
    :param namedtuples: Yield namedtuples.
    :param dicts: Yield dicts.
    :param encoding: Encoding of the content.
    :param kw: Keyword parameters are passed through to csv.reader. Note that as opposed\
    to csv.reader delimiter defaults to '\t' not ','.
    :return: A generator over the rows.
    """
    # Either namedtuples or dicts can be chosen as output format.
    assert not (namedtuples and dicts)

    # for backward compatibility with the rows function:
    kw.setdefault('delimiter', '\t')

    # We make sure format parameters for the underlying reader have the correct type.
    for name in 'delimiter quotechar escapechar'.split():
        c = kw.get(name)
        if c and PY2 and isinstance(c, text_type):
            kw[name] = to_binary(c)

    if namedtuples:
        _reader = NamedTupleReader
    elif dicts:
        _reader = UnicodeDictReader
    else:
        _reader = UnicodeReader

    with _reader(lines_or_file, encoding=encoding, **kw) as r:
        for item in r:
            yield item
