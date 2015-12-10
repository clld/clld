import unittest

from clld.tests.util import TESTS_DIR


class Tests(unittest.TestCase):
    def test_get_config(self):
        from clld.config import get_config

        cfg = get_config(TESTS_DIR.joinpath('test.ini').as_posix())
        self.assertEqual(cfg['app:main.custom_int'], 5)
