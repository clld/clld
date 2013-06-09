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
        self.assertTrue(isinstance(co.span_attrs(), dict))
