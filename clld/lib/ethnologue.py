"""
functionality to gather information to link to ethnologue.com
"""
import re
import time

import requests
from bs4 import BeautifulSoup as bs


def get(path):
    """retrieve a resource from the ethnologue site and return it's representation.
    """
    return requests.get("http://ethnologue.com" + path).content


def get_subgroups():
    prefix = '/subgroups/'

    def parse_subgroups(doc):
        for a in bs(doc).find_all('a', href=True):
            if a['href'].startswith(prefix):
                yield a.text.split('(')[0].strip(), a['href'][len(prefix):]

    res = dict(list(parse_subgroups(get('/browse/families'))))
    ids = res.values()
    res['docs'] = {}

    for id_ in ids:
        time.sleep(1)
        doc = get(prefix + id_)
        res.update(dict(list(parse_subgroups(doc))))
        res['docs'][id_] = doc

    return res


def get_classification(group, doc):
    prefix = '/subgroups/'
    res = {}
    psubgroupname = re.compile('(?P<name>[^\(]+)')
    pext = re.compile('\((?P<ext>[0-9]+)\)')

    def parse_languages(node):
        """
        <span class="field-content">Chinese, Gan <a href="/language/gan">[gan]</a>
        """
        for a in node.find_all('a', href=True):
            if a['href'].startswith('/language/'):
                yield (
                    a.text.split(']')[0].split('[')[1].strip(),
                    list(a.parent.stripped_strings)[0])

    def parse_subgroups(node):
        for a in node.find_all('a', href=True):
            if a['href'].startswith(prefix):
                yield a

    def parse_classification(a):
        root = None
        for p in a.parents:
            if p.name == 'li':
                root = p
                break
        assert root
        return (
            [aa['href'][len(prefix):] for aa in parse_subgroups(root)],
            list(parse_languages(root)))

    for a in parse_subgroups(bs(doc)):
        id_ = a['href'][len(prefix):]
        #print group, id_
        try:
            name = psubgroupname.match(a.text).group('name').strip()
            ext = int(pext.search(a.text).group('ext').strip())
        except:  # pragma: no cover
            print a.text
            raise
        subfamilies, languages = parse_classification(a)
        if ext != len(languages) and id_ not in [
            'mor-0', 'west-3', 'bole-proper', 'bai', 'atlantic-congo', 'east-16',
            'west-12', 'volta-congo', 'benue-congo', 'bantoid', 'southern'
        ]:  # pragma: no cover
            print group
            print id_
            print ext, len(languages)
        res[id_] = (name, subfamilies, languages)
