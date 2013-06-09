import unittest


class Tests(unittest.TestCase):
    def test_Record(self):
        from clld.lib.bibtex import Record

        rec = Record(
            'book', '1',
            title='The Title', editor='ed', booktitle='bt', school='s', issue='i',
            pages='1-4', publisher='M')
        self.assertTrue('@book' in rec.__unicode__())
        self.assertTrue('@book' in rec.__str__())
        self.assertTrue('The Title' in rec.text())
