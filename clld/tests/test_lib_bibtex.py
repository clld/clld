# coding: utf8
from __future__ import unicode_literals
import unittest

from mock import Mock

from clld.tests.util import TESTS_DIR


class Tests(unittest.TestCase):
    def test_unescape(self):
        from clld.lib.bibtex import unescape

        assert unescape(r"\ss ") == 'ß'

    def test_Record(self):
        from clld.lib.bibtex import Record, EntryType

        rec = Record(
            'book', '1',
            title='The Title',
            author='author',
            editor='ed',
            booktitle='bt',
            school='s',
            issue='i',
            pages='1-4',
            publisher='M',
            note="Revised edition")
        self.assertTrue('@book' in rec.__unicode__())
        self.assertTrue('@book' in rec.__str__())
        self.assertTrue('bt' in rec.text())

        for fmt in ['txt', 'en', 'ris', 'mods']:
            rec.format(fmt)

        rec = Record.from_string(rec.__unicode__(), lowercase=True)
        rec = Record.from_object(Mock())

        rec = Record(
            'incollection', '1',
            title='The Title', editor='ed', booktitle='bt', school='s', issue='i',
            pages='1-4', publisher='M', note="Revised edition")
        self.assertTrue('In ' in rec.text())

        rec = Record(
            'article', '1',
            title='The Title', journal='The Journal', volume="The volume", issue='issue')
        self.assertTrue('The Journal' in rec.text())

        rec = Record('xmisc', '1', note='Something')
        self.assertTrue(rec.genre == EntryType.misc)
        self.assertTrue('Something' in rec.text())

    def test_linearization(self):
        from clld.lib.bibtex import Record

        for bib, txt in [
            (
                """@book{Dayley-1985,
  address    = {Berkeley},
  author     = {Dayley, Jon P.},
  iso_code   = {tzt; tzj},
  olac_field = {general_linguistics; semantics; morphology; typology; syntax},
  publisher  = {University of California Press},
  series     = {University of California Publications in Linguistics},
  title      = {Tzutujil Grammar},
  volume     = {107},
  wals_code  = {tzu},
  year       = {1985}
}
                """,
                "Dayley, Jon P. 1985. Tzutujil Grammar. (University of California "
                "Publications in Linguistics, 107.) Berkeley: University of California "
                "Press."),
            (
                """@book{318762,
  address    = {Vancouver},
  author     = {Cook, Eung-Do},
  pages      = {670},
  publisher  = {UBC Press},
  series     = {First Nations Languages Series},
  title      = {A Tsilhqút'ín Grammar},
  year       = {2013}
}
                """,
                "Cook, Eung-Do. 2013. A Tsilhqút'ín Grammar. (First Nations Languages "
                "Series.) Vancouver: UBC Press. 670pp."),
            (
                """@inbook{316361,
  author     = {Healey, Alan},
  booktitle  = {New Guinea area languages and language study},
  pages      = {223-232},
  title      = {History of research in Austronesian languages: Admiralty Islands area},
  volume     = {2}
}
                """,
                "Healey, Alan. n.d. History of research in Austronesian languages: "
                "Admiralty Islands area. 2. 223-232.")
        ]:
            rec = Record.from_string(bib)
            self.assertEqual(rec.text(), txt)

    def test_Database(self):
        from clld.lib.bibtex import Record, Database

        db = Database([])
        self.assertEqual(len(db), 0)
        db = Database([Record('book', 'id')])
        self.assertEqual(db[0], db['id'])
        assert unicode(db)
        db = Database.from_file('notexisting.bib')
        self.assertEqual(len(db), 0)
        db = Database.from_file(TESTS_DIR.joinpath('test.bib'))
        self.assertEqual(len(db), 1)
        assert [r for r in db]
