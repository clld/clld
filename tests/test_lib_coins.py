import pytest

from clld.lib.bibtex import Record
from clld.lib.coins import ContextObject


@pytest.mark.parametrize(
    'sid,mtx,data,assertion',
    [
        ('sid', 'journal', [('jtitle', '\xe2')], lambda sa: '%C3%A2' in sa['title']),
        (
            'sid',
            'journal',
            [('jtitle', bytes('ä'.encode('utf8')))],
            lambda sa: '%C3%A4' in sa['title']),
        ('sid', 'book', [('btitle', 'the title')], lambda sa: bool(sa)),
        ('äöü', 'äöü', [], lambda sa: bool(sa)),
        ('äöü'.encode('latin1'), None, [], lambda sa: bool(sa)),
    ]
)
def test_ContextObject_span_attrs(sid,mtx,data,assertion):
    assert assertion(ContextObject(sid, mtx, *data).span_attrs())


@pytest.mark.parametrize(
    'genre,fields',
    [
        ('book', dict(title='The Title', author='L, F')),
        ('article', dict(title='The Title', author='The One and The Other', journal='J')),
        ('phdthesis', dict(title='The Title')),
        ('conference', dict(title='The Title', booktitle='something')),
    ]
)
def test_ContextObject_from_bibtex(genre, fields):
    co = ContextObject.from_bibtex('sid', Record(genre, '1', **fields))
    assert isinstance(co.span_attrs(), dict)
