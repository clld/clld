# coding: utf8
from __future__ import unicode_literals

from clldutils.testing import WithTempDir


class Tests(WithTempDir):
    def test_safe_overwrite(self):
        from clld.util import safe_overwrite

        target = self.tmp_path('a', 'b')
        with safe_overwrite(target) as tmp:
            with tmp.open('w', encoding='utf8') as fp:
                fp.write('stuff')

        self.assertFalse(tmp.exists())
        self.assertTrue(target.exists())

        with safe_overwrite(target) as tmp:
            with tmp.open('w', encoding='utf8') as fp:
                fp.write('other')

        with target.open(encoding='utf8') as fp:
            self.assertEqual(fp.read(), 'other')


def test_random_string():
    from clld.util import random_string

    assert len(random_string(5)) == 5


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

    db_type = A.db_type()
    assert A.val1 == db_type.process_result_value(
        db_type.process_bind_param(A.val1, None), None)
    assert db_type.process_result_value(
        db_type.process_bind_param(None, None), None) is None
    assert A.val1.__json__() == A.val1.__unicode__()
