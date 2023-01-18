from clld.util import *


def test_safe_overwrite(tmp_path):
    target = tmp_path / 'a' / 'b'
    with safe_overwrite(target) as tmp:
        tmp.write_text('stuff', encoding='utf8')

    assert not tmp.exists()
    assert target.exists()

    with safe_overwrite(target) as tmp:
        tmp.write_text('other', encoding='utf8')

    with target.open(encoding='utf8') as fp:
        assert fp.read() == 'other'


def test_random_string():
    assert len(random_string(5)) == 5


def test_summary():
    # text consisting of unique words
    text = "This is a long text, which we want to summarize."

    assert summary(text[:20]) == text[:20]
    assert summary(text, len(text) - 1).endswith('...')
    assert summary('One verylongword', 10) == 'One ...'
    assert summary('One verylongword', 2) == '...'


def test_DeclEnum():
    class A(DeclEnum):
        val1 = '1', 'value 1'
        val2 = '2', 'value 2'

    db_type = A.db_type()
    assert A.val1 == db_type.process_result_value(
        db_type.process_bind_param(A.val1, None), None)
    assert db_type.process_result_value(
        db_type.process_bind_param(None, None), None) is None
    assert A.val1.__json__() == str(A.val1)
