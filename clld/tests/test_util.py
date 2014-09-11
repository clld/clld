# coding: utf8
from __future__ import unicode_literals
from datetime import date
import random
from tempfile import mktemp

from six import binary_type
from path import path


def test_parse_json_with_datetime():
    from clld.util import parse_json_with_datetime

    assert parse_json_with_datetime(dict(d='2012-12-12T20:12:12.12'))['d'].year


def test_nfilter():
    from clld.util import nfilter

    assert nfilter(range(5)) == list(range(1, 5))


def test_json():
    from clld.util import jsondump, jsonload

    d = {'a': 234, 'ä': 'öäüß'}
    p = path(mktemp())
    jsondump(d, p)
    for k, v in jsonload(p).items():
        assert d[k] == v
    p.remove()


def test_encoded():
    from clld.util import encoded

    s = '\xe4'
    latin1 = binary_type(s.encode('latin1'))
    utf8 = binary_type(s.encode('utf8'))
    assert encoded(s) == utf8
    assert encoded(s, 'latin1') == latin1
    assert encoded(utf8) == utf8
    assert encoded(latin1) == utf8
    assert encoded(latin1, 'latin1') == latin1


def test_dict_merged():
    from clld.util import dict_merged

    assert dict_merged(None, a=1) == {'a': 1}
    assert dict_merged(None, a=1, _filter=lambda i: i != 1) == {}
    assert dict_merged(None, a=None) == {}


def test_cached_property():
    from clld.util import cached_property

    class C(object):
        @cached_property()
        def attr(self):
            return random.randint(1, 100000)

    c = C()
    call1 = c.attr
    assert call1 == c.attr
    del c._cache['attr']
    assert call1 != c.attr


def test_NoDefault():
    from clld.util import NO_DEFAULT

    def f(default=NO_DEFAULT):
        if default is NO_DEFAULT:
            return 0
        return default

    assert f() != f(default=None)
    assert repr(NO_DEFAULT)


def test_slug():
    from clld.util import slug

    assert slug('A B. \xe4C') == 'abac'


def test_DeclEnum():
    from clld.util import DeclEnum

    class A(DeclEnum):
        val1 = '1', 'value 1'
        val2 = '2', 'value 2'

    for val, desc in A:
        assert val == '1'
        break

    assert '1' in repr(A.val1)
    assert A.from_string('1') == A.val1
    try:
        A.from_string('x')
        assert False  # pragma: no cover
    except ValueError:
        assert True
    db_type = A.db_type()
    assert A.val1 == db_type.process_result_value(
        db_type.process_bind_param(A.val1, None), None)
    assert db_type.process_result_value(
        db_type.process_bind_param(None, None), None) is None
    assert A.val1.__json__() == A.val1.__unicode__()


def test_format_size():
    from clld.util import format_size

    for i in range(10):
        assert format_size(1000 ** i)


def test_format_json():
    from clld.util import format_json

    format_json(date.today())
