"""
support for reading and writing delimiter-separated value files.
"""
from collections import namedtuple

import unicsv


def normalize_name(s):
    """
    >>> assert normalize_name('class') == 'class_'
    >>> assert normalize_name('a-name') == 'a_name'
    """
    if s == 'class':
        return 'class_'
    return s.replace('-', '_').replace('.', '_')


def rows(filename=None,
         content=None,
         delimiter='\t',
         namedtuples=False,
         encoding=None,
         newline='\n'):
    """
    >>> assert list(rows(__file__))
    >>> from clld.tests.util import TESTS_DIR
    >>> l = list(rows(TESTS_DIR.joinpath('test.tab'), namedtuples=True, encoding='utf8'))
    >>> assert l
    """
    assert filename or content
    assert not (filename and content)
    cls = None
    fields = []

    if filename:
        with open(filename, 'r') as fp:
            content = fp.read()

    if encoding:
        content = content.decode(encoding)

    for i, line in enumerate(content.split(newline)):
        if not line.strip():
            continue
        row = [s.strip() for s in line.split(delimiter)]
        if namedtuples and i == 0:
            fields = row
            cls = namedtuple('Row', map(normalize_name, row))
        else:
            if fields:
                while len(row) < len(fields):
                    row.append(None)
            yield cls(*row) if cls else row


def namedtuples_from_csv(fp):
    reader = unicsv.UnicodeCSVDictReader(fp)
    c = namedtuple('Row', map(normalize_name, reader.fieldnames))
    for d in reader:
        yield c(**d)


UnicodeCsvWriter = unicsv.UnicodeCSVWriter
