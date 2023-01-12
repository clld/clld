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


def test_bibtex2source():
    bibtex2source(Record('book', 'id', author='M, R and G, H and Z, U'))
    bibtex2source(Record('book', 'id', editor='M, R and G, H'))
    bibtex2source(Record('book', 'id', title='tb', customfield='cf', year="1920}"))
    assert bibtex2source(Record('misc', 'Id', title='title')).id == 'Id'


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
