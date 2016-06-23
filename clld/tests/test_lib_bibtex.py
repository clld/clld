# coding: utf8
from __future__ import unicode_literals, division, print_function, absolute_import
import unittest

from six import text_type, binary_type
from mock import Mock

from clld.tests.util import TESTS_DIR


class Tests(unittest.TestCase):
    def test_unescape(self):
        from clld.lib.bibtex import unescape, u_unescape

        self.assertEqual(unescape(binary_type("\\ss \xef".encode('latin1'))), 'ß\xef')
        self.assertEqual(unescape("\\ss "), 'ß')
        self.assertEqual(u_unescape('?[\\u123] ?[\\u1234]'), '{ \u04d2')
        s = '\u2013'
        self.assertEqual(s, unescape(s))
        self.assertEqual(unescape('?[\\u65533]'), '\ufffd')

    def test_stripctrlchars(self):
        from clld.lib.bibtex import stripctrlchars

        self.assertEqual(stripctrlchars('a\u0008\u000ba'), 'aa')
        self.assertEqual(stripctrlchars(None), None)

    def test_Record(self):
        from clld.lib.bibtex import Record, EntryType

        rec = Record('article', '1', author=['a', 'b'], editor='a and b')
        self.assertEqual(rec['author'], 'a and b')
        self.assertEqual(rec.get('author'), rec.getall('author'))
        self.assertEqual(rec['editor'], rec.get('editor'))
        self.assertEqual(rec.getall('editor'), ['a', 'b'])

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
        self.assertIn('@book', rec.__unicode__())
        self.assertIn('@book', rec.__str__())
        self.assertIn('bt', rec.text())

        for fmt in ['txt', 'en', 'ris', 'mods']:
            rec.format(fmt)

        Record.from_string(rec.__unicode__(), lowercase=True)
        Record.from_object(Mock())

        rec = Record(
            'incollection', '1',
            title='The Title', editor='ed', booktitle='bt', school='s', issue='i',
            pages='1-4', publisher='M', note="Revised edition")
        self.assertIn('In ', rec.text())

        rec = Record(
            'article', '1',
            title='The Title', journal='The Journal', volume="The volume", issue='issue')
        self.assertTrue('The Journal' in rec.text())

        rec = Record('xmisc', '1', note='Something')
        self.assertEqual(rec.genre, EntryType.misc)
        self.assertIn('Something', rec.text())

    def test_Database(self):
        from clld.lib.bibtex import Record, Database

        db = Database([])
        self.assertEqual(len(db), 0)
        db = Database([Record('book', 'id')])
        self.assertEqual(db[0], db['id'])
        assert text_type(db)
        db = Database.from_file('notexisting.bib')
        self.assertEqual(len(db), 0)
        db = Database.from_file(TESTS_DIR.joinpath('test.bib'))
        self.assertEqual(len(db), 1)
        assert '@' in db[0]['title']
        assert [r for r in db]
        self.assertRaises(NotImplementedError, db.format, 'txt')
