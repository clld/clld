import pytest
from sqlalchemy import create_engine

import clld
from clld.lib.bibtex import Record


def test_data_file():
    from clld.scripts.util import data_file

    assert data_file(clld, 'util.py').stem == 'util'


def test_setup_session(testsdir):
    from clld.scripts.util import setup_session

    res = setup_session('{0}#main'.format(testsdir / 'test.ini'), create_engine('sqlite://'))
    assert res == 'tests'


def test_SessionContext(testsdir):
    from clld.scripts.util import SessionContext, get_env_and_settings

    _, settings = get_env_and_settings('{0}#main'.format(testsdir / 'test.ini'))
    with SessionContext(settings):
        pass


def test_bibtex2source():
    from clld.scripts.util import bibtex2source

    bibtex2source(Record('book', 'id', author='M, R and G, H and Z, U'))
    bibtex2source(Record('book', 'id', editor='M, R and G, H'))
    bibtex2source(Record('book', 'id', title='tb', customfield='cf', year="1920}"))
    assert bibtex2source(Record('misc', 'Id', title='title')).id == 'Id'


def test_parsed_args(testsdir):
    from clld.scripts.util import parsed_args

    parsed_args((['-x'], dict(default=None)), args=[str(testsdir / 'test.ini')])


def test_Data(mocker):
    from clld.db.models.common import Language
    from clld.scripts.util import Data

    session = set()
    mocker.patch('clld.scripts.util.DBSession', session)
    d = Data(jsondata={})
    d.add(Language, 'l', id='l', name='l')
    assert session
    d.add(Language, 'l2', _obj=5)
    with pytest.raises(ValueError):
        d.add(Language, 'l3', id='l.3')


def test_add_language_codes(env):
    from clld.db.models.common import Language
    from clld.scripts.util import Data, add_language_codes

    add_language_codes(Data(), Language(), 'iso', glottocodes=dict(iso='glot1234'))
