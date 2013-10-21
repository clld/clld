"""
support for reading and writing deimiter-separated value files.
"""
import csv
import codecs
import cStringIO
from collections import namedtuple


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
    >>> assert list(rows(TESTS_DIR.joinpath('test.tab'), namedtuples=True, encoding='utf8'))
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


class UnicodeCsvWriter:
    """A CSV writer which will write rows to CSV file object "fp",
    which is encoded in the given encoding.

    >>> fp = cStringIO.StringIO()
    >>> writer = UnicodeCsvWriter(fp)
    >>> writer.writerows([[1, u'\xef']])
    """

    def __init__(self, fp, dialect=csv.excel, encoding="utf-8", **kw):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kw)
        self.stream = fp
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow(
            [s.encode("utf-8") if hasattr(s, 'encode') else s for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
