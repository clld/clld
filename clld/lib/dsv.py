# coding: utf8
"""
Support for reading delimiter-separated value files.

This module contains unicode aware replacements for :func:`csv.reader`
and :func:`csv.writer`.  It was stolen/extracted from the ``csvkit``
project to allow re-use when the whole ``csvkit`` package isn't
required.

The original implementations were largely copied from
`examples in the csv module documentation <http://docs.python.org/library/csv.html#examples>`_.

.. seealso:: http://en.wikipedia.org/wiki/Delimiter-separated_values
"""
from __future__ import unicode_literals
import codecs
import csv
import fnmatch
from collections import namedtuple
import keyword
from string import ascii_letters

from six import string_types, text_type
from six.moves import cStringIO as StringIO
#import unicsv

from clld.util import slug, nfilter, to_binary


EIGHT_BIT_ENCODINGS = [
    'utf-8', 'u8', 'utf', 'utf8', 'latin-1', 'iso-8859-1', 'iso8859-1', '8859',
    'cp819', 'latin', 'latin1', 'l1']


class UTF8Recoder(object):  # pragma: no cover
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8.
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')


class UnicodeCSVReader(object):  # pragma: no cover
    """
    A CSV reader which will read rows from a file in a given encoding.
    """
    def __init__(self, f, encoding='utf-8', maxfieldsize=None, **kwargs):
        f = UTF8Recoder(f, encoding)

        self.reader = csv.reader(f, **kwargs)

        if maxfieldsize:
            csv.field_size_limit(maxfieldsize)

    def next(self):
        try:
            row = self.reader.next()
        except csv.Error as e:
            # Terrible way to test for this exception, but there is no subclass
            if fnmatch.fnmatch(str(e), 'field large[rt] than field limit *'):
                raise ValueError
            else:
                raise e

        return [text_type(s, 'utf-8') for s in row]

    def __iter__(self):
        return self

    @property
    def line_num(self):
        return self.reader.line_num


class UnicodeCSVWriter(object):  # pragma: no cover
    """
    A CSV writer which will write rows to a file in the specified encoding.

    NB: Optimized so that eight-bit encodings skip re-encoding. See:
        https://github.com/onyxfish/csvkit/issues/175
    """
    def __init__(self, f, encoding='utf-8', **kwargs):
        self.encoding = encoding
        self._eight_bit = (self.encoding.lower().replace('_', '-') in
                EIGHT_BIT_ENCODINGS)

        if self._eight_bit:
            self.writer = csv.writer(f, **kwargs)
        else:
            # Redirect output to a queue for reencoding
            self.queue = StringIO()
            self.writer = csv.writer(self.queue, **kwargs)
            self.stream = f
            self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        if self._eight_bit:
            self.writer.writerow([text_type(s if s != None else '')
                    .encode(self.encoding) for s in row])
        else:
            self.writer.writerow([text_type(s if s != None else '')
                    .encode('utf-8') for s in row])
            # Fetch UTF-8 output from the queue...
            data = self.queue.getvalue()
            data = data.decode('utf-8')
            # ...and reencode it into the target encoding
            data = self.encoder.encode(data)
            # write to the file
            self.stream.write(data)
            # empty the queue
            self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UnicodeCSVDictReader(csv.DictReader):  # pragma: no cover
    """
    Defer almost all implementation to :class:`csv.DictReader`, but wraps our unicode reader instead
    of :func:`csv.reader`.
    """
    def __init__(self, f, fieldnames=None, restkey=None, restval=None, *args, **kwargs):
        reader = UnicodeCSVReader(f, *args, **kwargs)

        if 'encoding' in kwargs:
            kwargs.pop('encoding')

        csv.DictReader.__init__(self, f, fieldnames, restkey, restval, *args, **kwargs)

        self.reader = reader


class UnicodeCSVDictWriter(csv.DictWriter):  # pragma: no cover
    """
    Defer almost all implementation to :class:`csv.DictWriter`, but wraps our unicode writer instead
    of :func:`csv.writer`.
    """
    def __init__(self, f, fieldnames, writeheader=False, restval="", extrasaction="raise", *args, **kwds):
        self.fieldnames = fieldnames
        self.restval = restval

        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError("extrasaction (%s) must be 'raise' or 'ignore'" %
                   extrasaction)

        self.extrasaction = extrasaction

        self.writer = UnicodeCSVWriter(f, *args, **kwds)

        if writeheader:
            self.writerow(dict(zip(self.fieldnames, self.fieldnames)))


def normalize_name(s):
    """This function is called to convert ASCII strings to something that can pass as
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
    """
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
        if c and isinstance(c, text_type):
            kw[name] = to_binary(c)

    if isinstance(lines_or_file, string_types):
        # If a file name or path object is passed, we read the whole thing into a list of
        # lines, to make sure the file handle is closed right away.
        if 'lineterminator' in kw:
            with open(lines_or_file, mode='r') as fp:
                lines_or_file = fp.read().split(str(kw['lineterminator']))
        else:
            with open(lines_or_file, mode='rU') as fp:
                lines_or_file = [l[:-1] if l and l[-1] == str('\n') else l for l in fp]
    if isinstance(lines_or_file, list):
        # unicsv.UnicodeCSVReader does not support reading from arbitrary iterables such
        # as lists, but insists on calling a 'read' method.
        if encoding is None \
                or (lines_or_file and isinstance(lines_or_file[0], text_type)):
            lines_or_file = [l.encode('utf8') for l in lines_or_file]
            encoding = 'utf8'
        lines_or_file = StringIO(str('\n').join(nfilter(lines_or_file)))

    if dicts or namedtuples:
        impl = UnicodeCSVDictReader
        #impl = unicsv.UnicodeCSVDictReader
    else:
        impl = UnicodeCSVReader
        #impl = unicsv.UnicodeCSVReader
    res = impl(lines_or_file, encoding=encoding, **kw)
    if namedtuples:
        class_ = namedtuple('Row', map(normalize_name, res.fieldnames))
        for d in res:
            for n in res.fieldnames:
                d.setdefault(n, None)
            yield class_(**{normalize_name(k): v for k, v in d.items()})
    else:
        for d in res:
            yield d


UnicodeCsvWriter = UnicodeCSVWriter
#UnicodeCsvWriter = unicsv.UnicodeCSVWriter
