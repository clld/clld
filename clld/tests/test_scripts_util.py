import unittest

from path import path

import clld


class Tests(unittest.TestCase):
    def test_parsed_args(self):
        from clld.scripts.util import parsed_args

        parsed_args(args=[path(clld.__file__).dirname().joinpath('tests', 'test.ini')])
