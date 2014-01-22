from __future__ import unicode_literals
import unittest

from sqlalchemy.orm import joinedload
from path import path
from mock import patch, Mock

import clld
from clld.lib.bibtex import Record
from clld.tests.util import TestWithEnv


class Tests(unittest.TestCase):
    def test_bibtex2source(self):
        from clld.scripts.util import bibtex2source

        bibtex2source(Record('book', 'id', title='tb', customfield='cf', year="1920}"))

    def test_parsed_args(self):
        from clld.scripts.util import parsed_args

        parsed_args(args=[path(clld.__file__).dirname().joinpath('tests', 'test.ini')])

    def test_Data(self):
        from clld.db.models.common import Language
        from clld.scripts.util import Data

        session = set()
        with patch('clld.scripts.util.DBSession', session):
            d = Data(jsondata={})
            d.add(Language, 'l', id='l', name='l')
            assert session
            d.add(Language, 'l2', _obj=5)

    def test_add_language_codes(self, ):
        from clld.db.models.common import Language
        from clld.scripts.util import Data, add_language_codes

        add_language_codes(Data(), Language(), 'iso', glottocodes=dict(iso='glot1234'))


class Tests2(TestWithEnv):
    def test_index(self):
        from clld.db.models.common import Language
        from clld.scripts.util import index

        index(
            Language,
            self.env['request'],
            Mock(update=Mock(return_value=Mock(status=200))),
            query_options=[joinedload(Language.languageidentifier)])
