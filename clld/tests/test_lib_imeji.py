from __future__ import unicode_literals
import unittest

from clld.tests.util import TESTS_DIR


class Tests(unittest.TestCase):
    def test_Result(self):
        from clld.lib.imeji import file_urls

        res = list(file_urls(TESTS_DIR.joinpath('imeji_items.xml').as_posix()))
        self.assertEqual(len(res), 6)
