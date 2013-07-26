import unittest

from mock import Mock


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

        for fmt in ['txt', 'en', 'ris', 'mods']:
            rec.format(fmt)

        rec = Record.from_string(rec.__unicode__())
        rec = Record.from_object(Mock())
