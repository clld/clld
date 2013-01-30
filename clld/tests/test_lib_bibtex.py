import unittest


class Tests(unittest.TestCase):
    def test_Record(self):
        from clld.lib.bibtex import Record

        rec = Record('book', '1', title='The Title')
        self.assert_('@book' in rec.serialize())

