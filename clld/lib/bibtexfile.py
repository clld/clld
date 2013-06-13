"""
provides basic bibtex handling functionality

 notes:
 - the bibtex parser implemented in BibtexRecord is a very simple one.
   therefore, bibfiles may have to be preprocessed (for example with bibtool)
   before serving them to BibtexDatabase.
 - while the record storage in BibtexDatabase is implemented as list, thus
   mutable, it is not intended to allow adding or deleting records in a
   bibtex database. altering record content (but not there citation key) on
   the other hand is ok.
"""
from __future__ import unicode_literals
import re
import codecs

from path import path

from clld.lib.bibtex import Record


class BibtexDatabase:
    """
    a class to handle bibtex databases, i.e. a container class for BibtexRecord
    instances.
    """
    def __init__(self, bibFile, encoding='utf8'):
        """
        a bibtex database is defined by a bib-file

        @param bibFile: path of the bibtex-database-file to be read.

        >>> import tempfile
        >>> f = tempfile.mktemp('.bib')
        >>> db = BibtexDatabase(f)
        >>> db.append(TEST_RECORD)
        >>> assert 'new_key' in db.keys()
        >>> db['new_key']['title'] = 'some title'
        >>> try:
        ...   db.append(TEST_RECORD.replace('new_key', db[0].id))
        ... except ValueError:
        ...   print 'ok'
        ok
        >>> del db['new_key']
        >>> assert 'new_key' not in db.keys()
        """
        if path(bibFile).exists():
            with codecs.open(bibFile, encoding=encoding) as fp:
                content = fp.read()
        else:
            content = ''

        self._records = [Record.from_string('@' + r) for r in content.split('@')[1:]]

        # we also construct a mapping table for easy record lookup by citation
        # key and look for duplicate citation keys:
        self._buildKeyMap()
        return

    def _buildKeyMap(self):
        self._keyMap = {}
        for i in range(len(self._records)):
            key = self._records[i].id
            if key in self._keyMap:
                raise Exception('duplicate citation key: %s' % key)
            self._keyMap[key] = i
        return

    def append(self, record):
        if isinstance(record, basestring):
            record = Record.from_string(record)

        if record.id in self._keyMap:
            raise ValueError

        self._records.append(record)
        self._buildKeyMap()

    def __delitem__(self, key):
        if isinstance(key, int):
            del self._records[key]
        elif key in self._keyMap:
            del self._records[self._keyMap[key]]
        else:
            raise KeyError(key)
        self._buildKeyMap()

    def __getitem__(self, key):
        """to access bib records by index or citation key"""
        if isinstance(key, int):
            return self._records[key]

        if key in self._keyMap:
            return self._records[self._keyMap[key]]

        raise KeyError(key)

    def __iter__(self):
        return iter(self._records)

    def __len__(self):
        return len(self._records)

    def sort(self):
        self._records.sort()
        self._buildKeyMap()

    def keys(self):
        return self._keyMap.keys()

    def indexFromKey(self, key):
        # one might only be interested in the index, not the whole record!
        return get(self._keyMap, key, -1)


TEST_U_VALUE = 'M\xfcller'
TEST_RECORD = """\
@article{new_key,
}"""
