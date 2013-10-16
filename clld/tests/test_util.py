from __future__ import unicode_literals
from datetime import date


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
