from __future__ import unicode_literals

from sqlalchemy.orm.exc import NoResultFound

from clld.tests.util import TestWithDb
from clld.db.models.common import Language
from clld.db.meta import DBSession, VersionedDBSession


class Tests(TestWithDb):

    def test_JSONEncodedDict(self):
        l = Language(id='abc', name='Name', jsondata={'i': 2})
        DBSession.add(l)
        DBSession.flush()

        DBSession.expunge(l)
        for lang in DBSession.query(Language).filter(Language.id == 'abc'):
            self.assertEqual(lang.jsondata['i'], 2)
            break

    def test_CustomModelMixin(self):
        from clld.tests.fixtures import CustomLanguage

        DBSession.add(CustomLanguage(id='abc', name='Name', custom='c'))
        DBSession.flush()
        for lang in DBSession.query(Language).filter(Language.id == 'abc'):
            self.assertEqual(lang.custom, 'c')
            self.assertTrue('custom_t' in lang.__solr__(None))
            break

    def test_Base(self):
        l = Language(id='abc', name='Name')
        VersionedDBSession.add(l)
        VersionedDBSession.flush()
        VersionedDBSession.expunge(l)
        #print('pk: %s' % l.pk)
        #transaction.commit()
        #transaction.begin()
        #l = VersionedDBSession.query(Language).get(1)
        #print(l)
        #l.name = 'New name'
        #print('pk: %s' % l.pk)
        #transaction.commit()
        #transaction.begin()
        l = Language.get('abc')
        #print(l.version)
        self.assertEqual(l.name, 'Name')
        l.history()

        # a bit of a hack to test the human readable representations.
        # we exploit the fact, that on py2, string and unicode comparison does type
        # coercion, while on py3, the two methods should actualy return the same string.
        self.assertEqual(l.__str__(), l.__unicode__())
        Language().__str__()

    def test_Base_jsondata(self):
        l = Language(id='abc', name='Name')
        VersionedDBSession.add(l)
        VersionedDBSession.flush()
        l.update_jsondata(a=1)
        self.assertTrue('a' in l.jsondata)
        l.update_jsondata(b=1)
        self.assertTrue('b' in l.jsondata and 'a' in l.jsondata)
        self.assertTrue('b' in l.__json__(None)['jsondata'])

    def test_Base_get(self):
        self.assertEqual(42, Language.get('doesntexist', default=42))
        self.assertRaises(NoResultFound, Language.get, 'doesntexist')
