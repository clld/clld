# coding: utf8
from __future__ import unicode_literals, division, print_function, absolute_import

import pytest

from six import text_type, binary_type
from mock import Mock

from clld.lib.bibtex import *


@pytest.mark.parametrize(
    "arg,res",
    [
        (binary_type("\\ss \xef".encode('latin1')), 'ß\xef'),
        ("\\ss ", 'ß'),
        ('\u2013', '\u2013'),
        ('?[\\u65533]', '\ufffd'),
    ])
def test_unescape(arg, res):
    assert unescape(arg) == res


def test_u_unescape():
    assert u_unescape('?[\\u123] ?[\\u1234]') == '{ \u04d2'


def test_stripctrlchars():
    assert stripctrlchars('a\u0008\u000ba') == 'aa'
    assert stripctrlchars(None) is None


def test_Record_author_editor():
    rec = Record('article', '1', author=['a', 'b'], editor='a and b')
    assert rec['author'] == 'a and b'
    assert rec.get('author') == rec.getall('author')
    assert rec['editor'] == rec.get('editor')
    assert rec.getall('editor') == ['a', 'b']


def test_Record():
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
    assert '@book' in rec.__unicode__()
    assert '@book' in rec.__str__()
    assert 'bt' in rec.text()

    for fmt in ['txt', 'en', 'ris', 'mods']:
        rec.format(fmt)

    Record.from_string(rec.__unicode__(), lowercase=True)
    Record.from_object(Mock())

    rec = Record(
        'incollection', '1',
        title='The Title', editor='ed', booktitle='bt', school='s', issue='i',
        pages='1-4', publisher='M', note="Revised edition")
    assert 'In ' in rec.text()

    rec = Record(
        'article', '1',
        title='The Title', journal='The Journal', volume="The volume", issue='issue')
    assert 'The Journal' in rec.text()

    rec = Record('xmisc', '1', note='Something')
    assert rec.genre == EntryType.misc
    assert 'Something' in rec.text()


def test_Database(testsdir):
    db = Database([])
    assert not len(db)
    db = Database([Record('book', 'id')])
    assert db[0] == db['id']
    assert text_type(db)
    db = Database.from_file('notexisting.bib')
    assert not len(db)
    db = Database.from_file(testsdir / 'test.bib')
    assert len(db) == 1
    assert '@' in db[0]['title']
    assert [r for r in db]
    with pytest.raises(NotImplementedError):
        db.format('txt')
