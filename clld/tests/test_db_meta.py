from __future__ import unicode_literals

from sqlalchemy import Column, Integer, ForeignKey, Unicode

from clld.tests.util import TestWithDb
from clld.db.models.common import Language
from clld.db.meta import DBSession


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
        from clld.tests.util import CustomLanguage

        DBSession.add(CustomLanguage(id='abc', name='Name', custom='c'))
        DBSession.flush()
        for lang in DBSession.query(Language).filter(Language.id == 'abc'):
            self.assertEqual(lang.custom, 'c')
            break

    def test_Base(self):
        l = Language(id='abc', name='Name')
        DBSession.add(l)
        DBSession.flush()
        DBSession.expunge(l)
        self.assertEqual(Language.get('abc').name, 'Name')
