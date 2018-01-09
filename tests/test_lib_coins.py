# coding: utf8
from __future__ import unicode_literals

from six import binary_type

from clld.lib.bibtex import Record


def test_ContextObject():
    from clld.lib.coins import ContextObject

    c = ContextObject('sid', 'journal', ('jtitle', '\xe2'))
    assert '%C3%A2' in c.span_attrs()['title']
    c = ContextObject('sid', 'journal', ('jtitle', binary_type('ä'.encode('utf8'))))
    assert '%C3%A4' in c.span_attrs()['title']

    bib = Record('book', '1', title='The Title', author='L, F')
    ContextObject('sid', 'book', ('btitle', 'the title'))
    ContextObject.from_bibtex('sid', bib)
    bib = Record('article', '1',
                 title='The Title', author='The One and The Other', journal='J')
    ContextObject.from_bibtex('sid', bib)
    bib = Record('phdthesis', '1', title='The Title')
    ContextObject.from_bibtex('sid', bib)
    bib = Record('conference', '1', title='The Title', booktitle='something')
    co = ContextObject.from_bibtex('sid', bib)
    assert isinstance(co.span_attrs(), dict)

    assert ContextObject('äöü', 'äöü').span_attrs()
    assert ContextObject('äöü'.encode('latin1'), None).span_attrs()
