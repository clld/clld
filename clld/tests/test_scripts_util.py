from __future__ import unicode_literals
import unittest
from json import loads

from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload
from mock import patch, Mock

import clld
from clld.lib.bibtex import Record
from clld.tests.util import TestWithEnv, TESTS_DIR, WithDbAndDataMixin


class Tests(unittest.TestCase):
    def test_data_file(self):
        from clld.scripts.util import data_file

        self.assertEquals(data_file(clld, 'util.py').stem, 'util')

    def test_setup_session(self):
        from clld.scripts.util import setup_session

        res = setup_session(
            '%s#main' % TESTS_DIR.joinpath('test.ini').as_posix(),
            create_engine('sqlite://'))
        self.assertEquals(res, 'tests')

    def test_bibtex2source(self):
        from clld.scripts.util import bibtex2source

        bibtex2source(Record('book', 'id', author='M, R and G, H and Z, U'))
        bibtex2source(Record('book', 'id', editor='M, R and G, H'))
        bibtex2source(Record('book', 'id', title='tb', customfield='cf', year="1920}"))

    def test_parsed_args(self):
        from clld.scripts.util import parsed_args

        parsed_args(args=[TESTS_DIR.joinpath('test.ini').as_posix()])

    def test_glottocodes_by_isocode(self):
        from clld.scripts.util import glottocodes_by_isocode

        ce = Mock(return_value=Mock(execute=lambda *args: [('iso', 'abcd1234')]))

        with patch('clld.scripts.util.create_engine', ce):
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

        class Req(Mock):
            def get(self, *args):
                return Mock(json=Mock(return_value=loads(json)))

        with patch('clld.scripts.util.requests', Req()):
            assert glottocodes_by_isocode(
                None, cols=['id', 'latitude'])['aiw'][0] == 'aari1239'

    def test_Data(self):
        from clld.db.models.common import Language
        from clld.scripts.util import Data

        session = set()
        with patch('clld.scripts.util.DBSession', session):
            d = Data(jsondata={})
            d.add(Language, 'l', id='l', name='l')
            assert session
            d.add(Language, 'l2', _obj=5)
            self.assertRaises(ValueError, d.add, Language, 'l3', id='l.3')

    def test_add_language_codes(self, ):
        from clld.db.models.common import Language
        from clld.scripts.util import Data, add_language_codes

        add_language_codes(Data(), Language(), 'iso', glottocodes=dict(iso='glot1234'))


class Tests2(WithDbAndDataMixin, TestWithEnv):
    def test_index(self):
        from clld.db.models.common import Language
        from clld.scripts.util import index

        index(
            Language,
            self.env['request'],
            Mock(update=Mock(return_value=Mock(status=200))),
            query_options=[joinedload(Language.languageidentifier)])
