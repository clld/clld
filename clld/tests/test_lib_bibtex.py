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
