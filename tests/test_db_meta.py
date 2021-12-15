import json

import pytest
from sqlalchemy.orm.exc import NoResultFound

from clld.db.models.common import Language
from clld.db.meta import DBSession, is_base


def test_JSONEncodedDict(db):
    l = Language(id='abc', name='Name', jsondata={'i': 2})
    DBSession.add(l)
    DBSession.flush()

    DBSession.expunge(l)
    for lang in DBSession.query(Language).filter(Language.id == 'abc'):
        assert lang.jsondata['i'] == 2
        break


def test_CustomModelMixin(db, custom_language):
    DBSession.add(custom_language(id='abc', name='Name', custom='c'))
    DBSession.flush()
    for lang in DBSession.query(Language).filter(Language.id == 'abc'):
        assert lang.custom == 'c'
        break


def test_CustomModelMixin_polymorphic(db, custom_language):
    lang = Language(id='def', name='Name')
    assert repr(lang).startswith("<Language ")
    assert is_base(Language)
    assert not is_base(custom_language)
    clang = custom_language(id='abc', name='Name', custom='c')
    DBSession.add_all([lang, clang])
    DBSession.flush()
    DBSession.expunge_all()
    lang = DBSession.query(Language).filter_by(id='def').one()
    clang = DBSession.query(Language).filter_by(id='abc').one()

    assert lang.polymorphic_type == 'base'
    assert clang.polymorphic_type == 'custom'
    assert type(lang) is Language
    assert type(clang) is custom_language


def test_CsvMixin(db):
    l1 = Language(id='abc', name='Name', latitude=12.4, jsondata=dict(a=None))
    DBSession.add(l1)
    DBSession.flush()
    l1 = Language.csv_query(DBSession).first()
    cols = l1.csv_head()
    row = l1.to_csv()
    for k, v in zip(cols, row):
        if k == 'jsondata':
            assert 'a' in json.loads(v)


def test_CsvMixin2(db):
    from clld.db.meta import CsvMixin

    class B(object):
        id = 5

    class A(CsvMixin):
        b = None
        bs = None

        def __init__(self, b=None):
            if b:
                self.b = b
                self.bs = [b, b]

        def csv_head(self):
            return ['b__id', 'bs__ids']

    a = A(B())
    assert a.to_csv() == [5, "5,5"]


def test_Base(db):
    l = Language(id='abc', name='Name')
    DBSession.add(l)
    DBSession.flush()
    DBSession.expunge(l)
    l = Language.get('abc', session=DBSession)
    assert l.name == 'Name'

    Language().__str__()
    assert repr(l) == "<Language 'abc'>"


def test_Base_jsondata(db):
    l = Language(id='abc', name='Name')
    DBSession.add(l)
    DBSession.flush()
    l.update_jsondata(a=1)
    assert 'a' in l.jsondata
    l.update_jsondata(b=1)
    assert 'b' in l.jsondata and 'a' in l.jsondata
    assert 'b' in l.__json__(None)['jsondata']


def test_Base_get(db):
    assert 42 == Language.get('doesntexist', default=42)
    with pytest.raises(NoResultFound):
        Language.get('doesntexist')
