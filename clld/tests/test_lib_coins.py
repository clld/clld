# coding: utf8
from __future__ import unicode_literals
import unittest

from six import binary_type

from clld.lib.bibtex import Record


class Tests(unittest.TestCase):
    def test_ContextObject(self):
        from clld.lib.coins import ContextObject

        c = ContextObject('sid', 'journal', ('jtitle', '\xe2'))
        self.assertIn('%C3%A2', c.span_attrs()['title'])
        c = ContextObject('sid', 'journal', ('jtitle', binary_type('ä'.encode('utf8'))))
        self.assertIn('%C3%A4', c.span_attrs()['title'])

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
        self.assertTrue(isinstance(co.span_attrs(), dict))

        assert ContextObject('äöü', 'äöü').span_attrs()
        assert ContextObject('äöü'.encode('latin1'), None).span_attrs()
