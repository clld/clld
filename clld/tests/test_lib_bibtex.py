import unittest


class Tests(unittest.TestCase):
    def test_Record(self):
        from clld.lib.bibtex import Record

        rec = Record('book', '1', title='The Title')
        self.assertTrue('@book' in rec.__unicode__())
        self.assertTrue('@book' in rec.__str__())
