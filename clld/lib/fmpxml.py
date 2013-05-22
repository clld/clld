"""Functionality to retrieve data from a FileMaker server using the
'Custom Web Publishing with XML' protocol.

see http://www.filemaker.com/support/product/docs/12/fms/fms12_cwp_xml_en.pdf
"""
from logging import getLogger
log = getLogger(__name__)

from xml.etree import cElementTree as et

import requests


class Result(object):
    """Parses a filemaker pro xml result.
    """
    def __init__(self, content):
        self._root = et.fromstring(content)
        fields = []
        for field in self._find('field', path='.//'):
            fields.append((field.get('NAME'), field.get('TYPE')))
        resultset = self._find('resultset', path='.//')[0]
        self.total = int(resultset.get('FOUND'))
        self.items = []
        for row in self._find('row', resultset):
            item = {}
            for i, col in enumerate(self._find('col', row)):
                name, type_ = fields[i]
                data = self._find('data', col)
                if data:
                    val = data[0].text
                else:
                    assert '::' in name
                    val = None
                if val and type_ == 'NUMBER':
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            #
                            # TODO: is there a better way to handle stuff like (24, 57)?
                            #
                            pass
                item[name] = val
            self.items.append(item)

    def _find(self, localname, e=None, path=''):
        e = e or self._root
        return e.findall(
            path + '{http://www.filemaker.com/fmpxmlresult}' + localname.upper())


class Client(object):
    """Client for FileMaker's 'Custom Web Publishing with XML' feature.
    """
    def __init__(self, host, db, user, password, limit=1000, cache=None):
        self.host = host
        self.db = db
        self.user = user
        self.password = password
        self.limit = limit
        self.cache = cache if cache is not None else {}

    def _get_batch(self, what, offset=0):
        print what, offset
        key = '%s-%s-%s' % (what, offset, self.limit)
        if key in self.cache.keys():
            xml = self.cache[key]
        else:
            print '-- from server'
            log.info('retrieving %s (%s to %s)' % (what, offset, offset + self.limit))
            res = requests.get(
                'http://%s/fmi/xml/FMPXMLRESULT.xml' % self.host,
                params={
                    '-db': self.db,
                    '-lay': what,
                    '-findall': '',
                    '-skip': str(offset),
                    '-max': str(self.limit)},
                auth=(self.user, self.password))
            xml = res.text.encode('utf8')
            self.cache[key] = xml
        return Result(xml)

    def get(self, what):
        items = []
        batch = self._get_batch(what)
        items.extend(batch.items)
        while len(items) < batch.total:
            batch = self._get_batch(what, offset=len(items))
            items.extend(batch.items)
        return items
