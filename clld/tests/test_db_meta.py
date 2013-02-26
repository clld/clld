from __future__ import unicode_literals

import transaction
from sqlalchemy import Column, Integer, ForeignKey, Unicode

from clld.tests.util import TestWithDb
from clld.db.models.common import Language, File
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

        f = File()
        self.assertEqual(f.history(), [])
