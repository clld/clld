from __future__ import unicode_literals

from sqlalchemy import Column, Integer, ForeignKey, Unicode

from clld.tests.util import TestWithDb


class Tests(TestWithDb):
    def test_JSONEncodedDict(self):
        from clld.db.models.common import Language
        from clld.db.meta import DBSession

        l = Language(id='abc', name='Name', jsondata={'i': 2})
        DBSession.add(l)
        DBSession.flush()
        DBSession.expunge(l)
        for lang in DBSession.query(Language).filter(Language.id == 'abc'):
            self.assertEqual(lang.jsondata['i'], 2)
            break

    def test_CustomModelMixin(self):
        from clld.tests.util import CustomLanguage
        from clld.db.models.common import Language
        from clld.db.meta import DBSession

        DBSession.add(CustomLanguage(id='abc', name='Name', custom='c'))
        DBSession.flush()
        for lang in DBSession.query(Language).filter(Language.id == 'abc'):
            self.assertEqual(lang.custom, 'c')
            break
