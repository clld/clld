# coding: utf8
from __future__ import unicode_literals
from unittest import TestCase
from StringIO import StringIO

from clld.tests.util import TESTS_DIR


class Tests(TestCase):
    def test_reader(self):
        from clld.lib.dsv import reader

        lines = ['first\tline', 'sücond\tläneß']
        encoded_lines = [l.encode('utf8') for l in lines]
        csv_lines = [l.replace('\t', ',') for l in lines]

        def check(r):
            res = list(r)
            assert len(res) == 2
            assert res[1][1] == 'läneß'

        check(reader(lines))
        for lt in ['\n', '\r\n', '\r']:
            check(reader(StringIO(str(lt).join(encoded_lines))))
        check(reader(TESTS_DIR.joinpath('csv.txt'), delimiter=','))

        res = list(reader(TESTS_DIR.joinpath('test.tab'), namedtuples=True))
        assert res[0].a_name == 'b'
        # Missing column values should be set to None:
        assert res[2].a_name is None

        r = list(reader(lines, dicts=True))
        assert len(r) == 1 and r[0]['first'] == 'sücond'
        r = list(reader(lines, namedtuples=True))
        assert len(r) == 1 and r[0].first == 'sücond'
        r = list(reader(csv_lines, namedtuples=True, delimiter=','))
        assert len(r) == 1 and r[0].first == 'sücond'
