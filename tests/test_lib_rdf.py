import itertools

import pytest

from clld.lib.rdf import *


@pytest.mark.parametrize(
    'name,url',
    [
        ('dcterms:title', 'http://purl.org/dc/terms/title'),
        ('noprefix:lname', 'noprefix:lname'),
        ('rdf:nolname', 'rdf:nolname'),
        ('nocolon', 'nocolon'),
    ]
)
def test_expand_prefix(name, url):
    assert str(expand_prefix(name)) == url


def test_url_for_qname():
    assert url_for_qname('dcterms:title') == 'http://purl.org/dc/terms/title'


@pytest.mark.parametrize(
    'subject,props,substring',
    [
        ('subject', [('foaf:name', 'a name'), ('foaf:homepage', 'http://example.org')], None),
        ('subject', [('rdf:about', 'x'), ('foaf:homepage', 'http://example.org')], None),
        ('subject', [('about', 'x'), ('foaf:homepage', 'http://example.org')], None),
        ('http://example.org', [('dcterms:title', 'ttt')], 'ttt'),
    ]
)
def test_properties_as_xml_snippet(subject,props,substring):
    p = properties_as_xml_snippet(subject, props)
    assert not substring or (substring in p)


@pytest.mark.parametrize(
    'from_,to_',
    [
        (f1, f2) for f1, f2 in
        itertools.product(list(FORMATS.keys()) + [None], repeat=2)
        if f1 not in {None, 'nt'} and f2 != 'nt'
    ]
)
def test_convert(from_, to_):
    convert(ClldGraph().serialize(format=from_), from_, to_)
