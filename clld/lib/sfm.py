"""Parsing SIL Standard Format (SFM) files."""
from __future__ import unicode_literals, print_function, absolute_import, division
import re
import mimetypes
from collections import defaultdict
from io import open

from path import path
from clld.util import UnicodeMixin


MARKER_PATTERN = re.compile('\\\\(?P<marker>[a-z_]+)(\s+|$)')


def marker_split(block):
    """generate marker, value pairs from a text block (i.e. a list of lines)."""
    marker = None
    value = []

    for line in block.split('\n'):
        line = line.strip()
        if line.startswith('\\_'):
            continue  # we simply ignore SFM header fields
        match = MARKER_PATTERN.match(line)
        if match:
            if marker:
                yield marker, '\n'.join(value)
            marker = match.group('marker')
            value = [line[match.end():]]
        else:
            value.append(line)
    if marker:
        yield marker, ('\n'.join(value)).strip()


class Entry(list, UnicodeMixin):

    """We store entries in SFM files as lists of (marker, value) pairs."""

    def markers(self):
        return set(k for k, v in self)

    def get(self, key, default=None):
        """Use get to retrieve the first value for a marker or None."""
        for k, v in self:
            if k == key:
                return v
        return default

    def getall(self, key):
        """Use getall to retrieve all values for a marker."""
        return [v for k, v in self if k == key]

    def __unicode__(self):
        lines = []
        for key, value in self:
            lines.append('%s %s' % (key, value))
        return '\n'.join('\\' + l for l in lines)


def parse(filename, encoding, entry_impl, entry_sep):
    """We assume entries in the file are separated by a blank line."""
    with open(filename, encoding=encoding) as fp:
        for block in fp.read().split(entry_sep):
            if block.strip():
                block = entry_sep + block
            else:
                continue  # pragma: no cover
            rec = entry_impl()
            for marker, value in marker_split(block.strip()):
                value = value.strip()
                if value:
                    rec.append((marker, value))
            if rec:
                yield rec


class Dictionary(object):

    """Represents lexical data from a SFM file."""

    def __init__(self,
                 filename,
                 encoding='utf8',
                 validate=True,
                 entry_impl=Entry,
                 entry_sep='\n\n'):
        self.filename = filename
        self.validate = validate
        self.dir = path(filename).dirname()
        self.entries = []
        self._markers = set()
        for entry in parse(filename, encoding, entry_impl, entry_sep):
            self._markers.update(entry.markers())
            self.entries.append(self.validated(entry))

    def markers(self):
        return self._markers

    def validated(self, entry):
        def basename(path):  # pragma: no cover
            if '\\' in path:
                return path.split('\\')[-1]
            if '/' in path:
                return path.split('/')[-1]
            return path

        if self.validate:
            for marker, subdir, mimetype in [
                ('pc', 'images', 'image'), ('sf', 'sounds', 'audio')
            ]:
                for i, pair in entry:
                    if pair[0] == marker:  # pragma: no cover
                        p = self.dir.joinpath(subdir, basename(pair[1]))
                        assert p.exists()
                        mtype, _ = mimetypes.guess_type(basename(pair[1]))
                        assert mtype.split('/')[0] == mimetype
                        entry[i] = (pair[0], (p, mtype))
        return entry

    def values(self, marker):
        """Compute simple stats for the values of marker.

        :return: dict of distinct values for marker with number of occurrences.
        """
        res = defaultdict(lambda: 0)
        for e in self.entries:
            for v in e.getall(marker):
                res[v] += 1
        return res
