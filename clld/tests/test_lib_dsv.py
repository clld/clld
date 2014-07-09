# coding: utf8
from __future__ import unicode_literals, print_function
from unittest import TestCase
from tempfile import mktemp

from six import PY3, BytesIO, StringIO
from path import path

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

        lines = ['first\tline', 'sücond\tläneß']
        encoded_lines = [l.encode('utf8') for l in lines]
        csv_lines = [l.replace('\t', ',') for l in lines]

        def check(r):
            res = list(r)
            assert len(res) == 2
            assert res[1][1] == 'läneß'

        check(reader(lines))
        for lt in ['\n', '\r\n', '\r']:
            if PY3:  # pragma: no cover
                # Simulate file opened in text mode:
                fp = StringIO(lt.join(lines), newline='')
            else:
                # Simulate file opened in binary mode:
                fp = BytesIO(to_binary(lt).join(encoded_lines))
            check(reader(fp))
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
        self.assertEqual(list(reader([], dicts=True)), [])
        self.assertEqual(list(reader([''], dicts=True, fieldnames=['a', 'b'])), [])
        self.assertEqual(list(reader(['a,b', ''], dicts=True)), [])

        r = reader(
            ['a,b', '1,2,3,4', '1'], dicts=True, restkey='x', restval='y', delimiter=',')
        self.assertEqual(list(r), [dict(a='1', b='2', x=['3', '4']), dict(a='1', b='y')])

    def test_writer(self):
        from clld.lib.dsv import UnicodeWriter

        row = [None, 0, 1.2, 'äöü']
        as_csv = ',0,1.2,äöü'

        with UnicodeWriter() as writer:
            writer.writerows([row])
        self.assertEqual(writer.read().splitlines()[0].decode('utf8'), as_csv)

        tmp = path(mktemp())
        with UnicodeWriter(tmp) as writer:
            writer.writerow(row)
        self.assertEqual(tmp.text(encoding='utf8').splitlines()[0], as_csv)
        tmp.remove()
