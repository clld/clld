from __future__ import unicode_literals
from json import loads

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload

import clld
from clld.lib.bibtex import Record


def test_data_file():
    from clld.scripts.util import data_file

    assert data_file(clld, 'util.py').stem == 'util'


def test_setup_session(testsdir):
    from clld.scripts.util import setup_session

    res = setup_session(
        '%s#main' % (testsdir / 'test.ini').as_posix(),
        create_engine('sqlite://'))
    assert res == 'tests'


def test_bibtex2source():
    from clld.scripts.util import bibtex2source

    bibtex2source(Record('book', 'id', author='M, R and G, H and Z, U'))
    bibtex2source(Record('book', 'id', editor='M, R and G, H'))
    bibtex2source(Record('book', 'id', title='tb', customfield='cf', year="1920}"))
    assert bibtex2source(Record('misc', 'Id', title='title')).id == 'Id'


def test_parsed_args(testsdir):
    from clld.scripts.util import parsed_args

    parsed_args(args=[(testsdir / 'test.ini').as_posix()])


def test_glottocodes_by_isocode(mocker, env):
    from clld.scripts.util import glottocodes_by_isocode

    ce = mocker.Mock(return_value=mocker.Mock(execute=lambda *args: [('iso', 'abcd1234')]))

    mocker.patch('clld.scripts.util.create_engine', ce)
    assert glottocodes_by_isocode('dburi')['iso'] == 'abcd1234'

    json = """{
        "properties": {
            "dataset": "glottolog",
            "uri_template": "http://glottolog.org/resource/languoid/id/{id}"
        },
        "resources": [
            {
                "id": "aant1238",
                "identifiers": [
                    {
                        "identifier": "tbg-aan",
                        "type": "multitree"
                    }
                ],
                "latitude": null,
                "longitude": null,
                "name": "Aantantara"
            },
            {
                "id": "aari1239",
                "identifiers": [
                    {
                        "identifier": "aiw",
                        "type": "iso639-3"
                    },
                    {
                        "identifier": "aiw",
                        "type": "multitree"
                    }
                ],
                "latitude": 5.95034,
                "longitude": 36.5721,
                "name": "Aari"
            }]}"""

    class Req(mocker.Mock):
        def get(self, *args):
            return mocker.Mock(json=mocker.Mock(return_value=loads(json)))

    mocker.patch('clld.scripts.util.requests', Req())
    assert glottocodes_by_isocode(None, cols=['id', 'latitude'])['aiw'][0] == 'aari1239'


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
