"""
support for reading and writing deimiter-separated value files.
"""
import csv
import codecs
import cStringIO


def rows(filename, delimiter='\t'):
    with open(filename, 'r') as fp:
        for line in fp:
            yield [s.strip() for s in line.split(delimiter)]


class UnicodeCsvWriter:
    """A CSV writer which will write rows to CSV file object "fp",
    which is encoded in the given encoding.
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
