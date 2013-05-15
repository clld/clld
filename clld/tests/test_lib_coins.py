import unittest

from clld.lib.bibtex import Record


class Tests(unittest.TestCase):
    def test_ContextObject(self):
        from clld.lib.coins import ContextObject

        bib = Record('book', '1', title='The Title')
        co = ContextObject('sid', 'book', ('btitle', 'the title'))
        co = ContextObject.from_bibtex('sid', bib)
