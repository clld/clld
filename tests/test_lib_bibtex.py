import pytest

from clld.lib.bibtex import *


@pytest.mark.parametrize(
    "arg,res",
    [
        (bytes("\\ss \xef".encode('latin1')), 'ß\xef'),
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
    assert rec['editor'] == rec.get('editor')
    assert rec.getall('editor') == ['a', 'b']


def test_Record(mocker):
    rec = Record('article', '1', author=['a', 'b'], editor='a and b')
    rec.format('txt')
    Record.from_string(str(rec), lowercase=True)
    Record.from_object(mocker.Mock())


@pytest.mark.parametrize(
    'genre,fields,expected_genre,substring',
    [
        (
            'incollection',
            dict(
                title='The Title',
                editor='ed',
                booktitle='bt',
                school='s',
                issue='i',
                pages='1-4',
                publisher='M',
                note="Revised edition"),
            EntryType.incollection,
            'In '),
        (
            'article',
            dict(
                title='The Title',
                journal='The Journal',
                volume="The volume",
                issue='issue'),
            EntryType.article,
            'The Journal'),
        ('xmisc', dict(note='Something'), EntryType.misc, 'Something'),
        (
            'book',
            dict(
                title='The Title',
                author='author',
                editor='ed',
                booktitle='bt',
                school='s',
                issue='i',
                pages='1-4',
                publisher='M',
                note="Revised edition"),
            EntryType.book,
            'bt'),
    ]
)
def test_Record_text(genre,fields,expected_genre,substring):
    rec = Record(genre, '1', **fields)
    assert expected_genre == rec.genre
    assert substring in rec.text()


def test_Database(testsdir):
    db = Database([])
    assert not len(db)
    db = Database([Record('book', 'id')])
    assert db[0] == db['id']
    assert str(db)
    db = Database.from_file('notexisting.bib')
    assert not len(db)
    db = Database.from_file(testsdir / 'test.bib')
    assert len(db) == 1
    assert '@' in db[0]['title']
    assert [r for r in db]
    with pytest.raises(NotImplementedError):
        db.format('txt')
