# coding: utf8
from __future__ import unicode_literals
from unittest import TestCase

from six import PY3
from six.moves import cStringIO as StringIO

from clld.util import to_binary
from clld.tests.util import TESTS_DIR


class Tests(TestCase):
    def test_normalize_name(self):
        from clld.lib.dsv import normalize_name

        assert normalize_name('class') == 'class_'
        assert normalize_name('a-name') == 'a_name'
        assert normalize_name('a näme') == 'a_name'
        assert normalize_name('Name') == 'Name'
        assert normalize_name('') == '_'
        assert normalize_name('1') == '_1'

    def test_reader(self):
        from clld.lib.dsv import reader

        if PY3:
            return

        lines = ['first\tline', 'sücond\tläneß']
        encoded_lines = [l.encode('utf8') for l in lines]
        csv_lines = [l.replace('\t', ',') for l in lines]

        def check(r):
            res = list(r)
            assert len(res) == 2
            assert res[1][1] == 'läneß'

        check(reader(lines))
        for lt in ['\n', '\r\n', '\r']:
            check(reader(StringIO(to_binary(lt).join(encoded_lines))))
        check(reader(TESTS_DIR.joinpath('csv.txt'), delimiter=','))

        res = list(reader(str(TESTS_DIR.joinpath('csv.txt')), lineterminator="#"))
        self.assertEquals(len(res), 2)

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
