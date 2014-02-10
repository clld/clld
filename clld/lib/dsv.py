# coding: utf8
"""
Support for reading and writing delimiter-separated value files.

.. seealso:: http://en.wikipedia.org/wiki/Delimiter-separated_values
"""
from __future__ import unicode_literals
from collections import namedtuple
from cStringIO import StringIO
import keyword
from string import ascii_letters

import unicsv

from clld.util import slug


def normalize_name(s):
    """This function is called to convert ASCII strings to something that can pass as
    python attribute name, to be used with namedtuples.

    >>> assert normalize_name('class') == 'class_'
    >>> assert normalize_name('a-name') == 'a_name'
    >>> assert normalize_name('a näme') == 'a_name'
    >>> assert normalize_name('Name') == 'Name'
    >>> assert normalize_name('') == '_'
    >>> assert normalize_name('1') == '_1'
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
        if c and isinstance(c, unicode):
            kw[name] = str(c)

    if isinstance(lines_or_file, basestring):
        # If a file name or path object is passed, we read the whole thing into a list of
        # lines, to make sure the file handle is closed right away.
        with open(lines_or_file, mode='rU') as fp:
            lines_or_file = [l[:-1] if l and l[-1] == str('\n') else l for l in fp]
    if isinstance(lines_or_file, list):
        # unicsv.UnicodeCSVReader does not support reading from arbitrary iterables such
        # as lists, but insists on calling a 'read' method.
        if encoding is None or (lines_or_file and isinstance(lines_or_file[0], unicode)):
            lines_or_file = [l.encode('utf8') for l in lines_or_file]
            encoding = 'utf8'
        lines_or_file = StringIO(str('\n').join(lines_or_file))

    if dicts or namedtuples:
        impl = unicsv.UnicodeCSVDictReader
    else:
        impl = unicsv.UnicodeCSVReader
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


UnicodeCsvWriter = unicsv.UnicodeCSVWriter
