from __future__ import unicode_literals

from clld.tests.util import TestWithDb, TestWithDbAndData
from clld import PY3


class Tests(TestWithDb):
    def test_Files(self):
        from clld.db.meta import DBSession
        from clld.db.models.common import Language, Language_files, File

        if PY3:
            return  # pragma: no cover

        l = Language(id='abc', name='Name')
        l.files.append(Language_files(name='abstract', file=File(content='c')))
        DBSession.add(l)
        DBSession.flush()
        DBSession.refresh(l)
        self.assertEqual(l.filesdict()['abstract'].content, 'c')

    def test_Data(self):
        from clld.db.meta import DBSession
        from clld.db.models.common import Language, Language_data

        l = Language(id='abc', name='Name')
        l.data.append(Language_data(key='abstract', value='c'))
        DBSession.add(l)
        DBSession.flush()
        DBSession.refresh(l)
        self.assertEqual(l.datadict()['abstract'], 'c')


class MoreTests(TestWithDbAndData):
    def test_Contribution(self):
        from clld.db.meta import DBSession
        from clld.db.models.common import Contribution

        c = DBSession.query(Contribution).first()
        self.assertTrue(c.primary_contributors)
        self.assertTrue(c.secondary_contributors)
