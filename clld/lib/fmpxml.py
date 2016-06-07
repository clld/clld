"""Functionality to retrieve data from a FileMaker server.

We use the FileMaker *Custom Web Publishing with XML* protocol.

.. seealso:: http://www.filemaker.com/support/product/docs/12/fms/fms12_cwp_xml_en.pdf
"""
from __future__ import print_function, unicode_literals, division, absolute_import
import re
from collections import OrderedDict

from bs4 import BeautifulSoup as bs
from logging import getLogger
log = getLogger(__name__)

from xml.etree import cElementTree as et

from six import text_type
import requests


FF = re.compile("font-family:\s*\'[^\']+\';\s*")
BOLD = re.compile("font-weight:\s*bold")
ITALIC = re.compile("font-style:\s*italic")
SC = re.compile("font-variant:\s*small\-caps")


def normalize_markup(s):
    """normalize markup in filemaker data."""
    if not s:
        return
    soup = bs(s.strip().replace('\n', ' ').replace('<BR>', '\n'), "html5lib")
    # remove empty, i.e. unstyled span tags
    for span in soup.find_all('span'):
        new_style = []
        style = span.attrs.get('style', '').strip()
        if BOLD.search(style):
            new_style.append('font-weight: bold;')
        if ITALIC.search(style):
            new_style.append('font-style: italic;')
        if SC.search(style):
            new_style.append('font-variant: small-caps;')
        if new_style:
            span['style'] = ' '.join(new_style)
        else:
            span.replace_with(span.string)

    res = text_type(soup.html.body).replace('<body>', '').replace('</body>', '')
    return res.replace('<p>', '').replace('</p>', '').strip() or None


class Result(object):

    """Represents a filemaker pro xml result."""

    def __init__(self, content):
        self._root = et.fromstring(content)
        fields = []
        for field in self._find('field', path='.//'):
            fields.append((field.get('NAME'), field.get('TYPE')))
        resultset = self._find('resultset', path='.//')[0]
        self.total = int(resultset.get('FOUND'))
        self.items = []
        for row in self._find('row', resultset):
            item = OrderedDict()
            for i, col in enumerate(self._find('col', row)):
                name, type_ = fields[i]
                data = self._find('data', col)
                if data:
                    val = data[0].text
                else:  # pragma: no cover
                    # make sure this is a derived value from a different table.
                    assert '::' in name
                    val = None
                if val and type_ == 'NUMBER':
                    try:
                        val = int(val)
                    except ValueError:  # pragma: no cover
                        try:
                            val = float(val)
                        except ValueError:
                            #
                            # TODO: is there a better way to handle stuff like (24, 57)?
                            #
                            pass
                item[name] = val
            self.items.append(item)

    def __iter__(self):
        return iter(self.items)

    def _find(self, localname, e=None, path=''):
        e = e or self._root
        return e.findall(
            path + '{http://www.filemaker.com/fmpxmlresult}' + localname.upper())


class Client(object):

    """Client for FileMaker's 'Custom Web Publishing with XML' feature."""

    def __init__(self, host, db, user, password, limit=1000, cache=None, verbose=True):
        self.host = host
        self.db = db
        self.user = user
        self.password = password
        self.limit = limit
        self.cache = cache if cache is not None else {}
        self.verbose = verbose

    def _get_batch(self, what, offset=0):
        if self.verbose:
            print(what, offset)  # pragma: no cover
        key = '%s-%s-%s' % (what, offset, self.limit)
        if key in self.cache.keys():
            xml = self.cache[key]
        else:
            if self.verbose:
                print('-- from server')  # pragma: no cover
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
        """Retrieve data from the server.

        :param what: Name of the layout from which to retrieve data.
        :return: ``list`` of ``dict`` representing the data of the layout.
        """
        items = []
        batch = self._get_batch(what)
        items.extend(batch.items)
        while len(items) < batch.total:
            batch = self._get_batch(what, offset=len(items))
            items.extend(batch.items)
        return items

    def get_layouts(self):  # pragma: no cover
        from PyFileMaker import FMServer

        fm = FMServer('%s:%s@%s' % (self.user, self.password, self.host))
        fm.setDb(self.db)
        return fm.getLayoutNames()
