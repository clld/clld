# coding: utf8
from __future__ import unicode_literals
import unittest

from clld.lib.bibtex import Record


class Tests(unittest.TestCase):
    def test_ContextObject(self):
        from clld.lib.coins import ContextObject

        bib = Record('book', '1', title='The Title', author='L, F')
        co = ContextObject('sid', 'book', ('btitle', 'the title'))
        co = ContextObject.from_bibtex('sid', bib)
        bib = Record('article', '1',
                     title='The Title', author='The One and The Other', journal='J')
        co = ContextObject.from_bibtex('sid', bib)
        bib = Record('phdthesis', '1', title='The Title')
        co = ContextObject.from_bibtex('sid', bib)
        bib = Record('conference', '1', title='The Title', booktitle='something')
        co = ContextObject.from_bibtex('sid', bib)
        self.assertTrue(isinstance(co.span_attrs(), dict))

        assert ContextObject('äöü', 'äöü').span_attrs()
        assert ContextObject('äöü'.encode('latin1'), None).span_attrs()
