import unittest

from path import path

import clld


class Tests(unittest.TestCase):
    def test_get_config(self):
        from clld.config import get_config

        cfg = get_config(path(clld.__file__).dirname().joinpath('tests', 'test.ini'))
        self.assertEqual(cfg['app:main.custom_int'], 5)
