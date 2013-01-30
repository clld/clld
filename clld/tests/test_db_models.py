from __future__ import unicode_literals

from clld.tests.util import TestWithDb, TestWithDbAndData


class Tests(TestWithDb):
    def test_Files(self):
        from clld.db.meta import DBSession
        from clld.db.models.common import Language, Language_files, File

        l = Language(id='abc', name='Name')
        l.files.append(Language_files(name='abstract', file=File(content='c')))
        DBSession.add(l)
        DBSession.flush()
        DBSession.refresh(l)
        self.assertEquals(l.filesdict()['abstract'].content, 'c')

    def test_Data(self):
        from clld.db.meta import DBSession
        from clld.db.models.common import Language, Language_data

        l = Language(id='abc', name='Name')
        l.data.append(Language_data(key='abstract', value='c'))
        DBSession.add(l)
        DBSession.flush()
        DBSession.refresh(l)
        self.assertEquals(l.datadict()['abstract'], 'c')


class MoreTests(TestWithDbAndData):
    def test_Contribution(self):
        from clld.db.meta import DBSession
        from clld.db.models.common import Contribution

        c = DBSession.query(Contribution).first()
        self.assert_(c.primary_contributors)
        self.assert_(c.secondary_contributors)
