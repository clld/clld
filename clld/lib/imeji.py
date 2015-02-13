"""
Utilities to manage multimedia files stored remotely in an imeji instance.

.. seealso:: http://imeji.org
"""
from __future__ import unicode_literals, print_function, absolute_import, division
from xml.etree import ElementTree


def qname(localname):
    return '{http://imeji.org/terms}' + localname


def get(e, k):
    return e.find(qname(k)).text


def file_urls(source):
    """Parse URL information from imeji XML.

    :param source: Path to a imeji collection metadata file in imeji XML format.
    :return: generator of infodicts.
    """
    for item in ElementTree.parse(source).findall(qname('item')):
        data = dict(
            id=item.attrib['id'],
            md5=get(item, 'checksum'),
            filename=get(item, 'filename'))
        for key in 'full web thumbnail'.split():
            data[key] = get(item, key + 'ImageUrl')
        # add an alias for the URL to the original file:
        data['url'] = data['full']
        yield data
