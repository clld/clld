import pytest
from sqlalchemy.exc import NoResultFound

from clld.db.models.common import Language
from clld.db.meta import DBSession, is_base


def test_JSONEncodedDict(db, persist):
    l = persist(Language(id='abc', name='Name', jsondata={'i': 2}))
    DBSession.expunge(l)
    for lang in DBSession.query(Language).filter(Language.id == 'abc'):
        assert lang.jsondata['i'] == 2
        break


def test_CustomModelMixin(db, custom_language, persist):
    persist(custom_language(id='abc', name='Name', custom='c'))
    for lang in DBSession.query(Language).filter(Language.id == 'abc'):
        assert lang.custom == 'c'
        break


def test_CustomModelMixin_polymorphic(db, custom_language, persist):
    lang = Language(id='def', name='Name')
    assert repr(lang).startswith("<Language ")
    assert is_base(Language)
    assert not is_base(custom_language)
    clang = custom_language(id='abc', name='Name', custom='c')
    persist(lang, clang)
    DBSession.expunge_all()
    lang = DBSession.query(Language).filter_by(id='def').one()
    clang = DBSession.query(Language).filter_by(id='abc').one()

    assert lang.polymorphic_type == 'base'
    assert clang.polymorphic_type == 'custom'
    assert type(lang) is Language
    assert type(clang) is custom_language


def test_Base(db, persist):
    l = persist(Language(id='abc', name='Name'))
    DBSession.expunge(l)
    l = Language.get('abc', session=DBSession)
    assert l.name == 'Name'

    Language().__str__()
    assert repr(l) == "<Language 'abc'>"


def test_Base_jsondata(db, persist):
    l = persist(Language(id='abc', name='Name'))
    l.update_jsondata(a=1)
    assert 'a' in l.jsondata
    l.update_jsondata(b=1)
    assert 'b' in l.jsondata and 'a' in l.jsondata
    assert 'b' in l.__json__(None)['jsondata']


def test_Base_get(db):
    assert 42 == Language.get('doesntexist', default=42)
    with pytest.raises(NoResultFound):
        Language.get('doesntexist')
