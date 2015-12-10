# coding: utf8
from __future__ import unicode_literals


def test_summary():
    from clld.util import summary

    # text consisting of unique words
    text = "This is a long text, which we want to summarize."

    assert summary(text[:20]) == text[:20]
    assert summary(text, len(text) - 1).endswith('...')
    assert summary('One verylongword', 10) == 'One ...'
    assert summary('One verylongword', 2) == '...'


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
