"""
Utilities to manage multimedia files stored remotely in an imeji instance.

.. seealso:: http://imeji.org
"""
from __future__ import unicode_literals, print_function, absolute_import, division
from xml.etree import ElementTree


qname = lambda localname: '{http://imeji.org/terms}' + localname


def get(e, k):
    return e.find(qname(k)).text


def file_urls(source):
    """Parse URL information from imeji XML.

    :param source: Path to a imeji collection metadata file in imeji XML format.
    :return: dict of (filename, infodict) pairs.
    """
    res = {}
    items = ElementTree.parse(source)
    for item in items.findall(qname('item')):
        data = dict(id=item.attrib['id'])
        for key in 'full web thumbnail'.split():
            data[key] = get(item, key + 'ImageUrl')
        # add an alias for the URL to the original file:
        data['url'] = data['full']
        res[get(item, 'filename')] = data
    return res
