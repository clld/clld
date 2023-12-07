import pytest
from pyramid.paster import get_appsettings

import clld
from clld.lib.bibtex import Record
from clld.cliutil import *
from clld.db.models.common import Language


def test_data_file():
    assert data_file(clld, 'util.py').stem == 'util'


def test_SessionContext(testsdir):
    settings = get_appsettings('{0}#main'.format(testsdir / 'test.ini'))
    with SessionContext(settings):
        pass


@pytest.mark.parametrize(
    'genre,id_,md,kw,assertion',
    [
        ('book', 'id', dict(author='M, R and G, H and Z, U'), None, None),
        ('book', 'id', dict(author='M, R and G, H'), None, None),
        ('book', 'id', dict(title='tb', customfield='cf', year="1920}"), None, None),
        ('misc', 'Id', dict(title='title'), None, lambda src: src.id == 'Id'),
        ('misc', 'Id', dict(title='title'), dict(lowercase_id=True), lambda src: src.id == 'id'),
        (
            'misc',
            'a-b',
            dict(url='https://example.org/~yurok/index.php'),
            dict(sluggify_id=False, latex_unescape=False),
            lambda src: src.id == 'a-b' and src.url == 'https://example.org/~yurok/index.php'),
    ]
)
def test_bibtex2source(genre, id_, md, kw, assertion):
    src = bibtex2source(Record(genre, id_, **md), **(kw or {}))
    if assertion:
        assert assertion(src)


def test_Data(mocker):
    session = set()
    mocker.patch('clld.cliutil.DBSession', session)
    d = Data(jsondata={})
    d.add(Language, 'l', id='l', name='l')
    assert session
    d.add(Language, 'l2', _obj=5)
    with pytest.raises(ValueError):
        d.add(Language, 'l3', id='l.3')


def test_add_language_codes(env):
    add_language_codes(Data(), Language(), 'iso', glottocodes=dict(iso='glot1234'))
