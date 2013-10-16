import unittest

from path import path
from mock import patch

import clld


class Tests(unittest.TestCase):
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
