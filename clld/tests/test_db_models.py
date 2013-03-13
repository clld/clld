from __future__ import unicode_literals

from six import PY3

from clld.tests.util import TestWithDb, TestWithDbAndData


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

    def test_UnitValue(self):
        from clld.db.meta import DBSession
        from clld.db.models.common import UnitParameter, UnitValue, UnitDomainElement

        p1 = UnitParameter()
        p2 = UnitParameter()
        v = UnitValue(
            unitdomainelement=UnitDomainElement(unitparameter_pk=p1.pk, name='ude'))
        self.assertEqual(str(v), 'ude')
        DBSession.add(v)
        DBSession.add(p2)
        DBSession.flush()
        try:
            v.unitparameter_pk = p2.pk
            raise ValueError  # pragma: no cover
        except AssertionError:
            pass

        v.unitparameter_pk = p1.pk
        DBSession.flush()


class MoreTests(TestWithDbAndData):
    def test_Contribution(self):
        from clld.db.meta import DBSession
        from clld.db.models.common import Contribution

        c = DBSession.query(Contribution).first()
        self.assertTrue(c.primary_contributors)
        self.assertTrue(c.secondary_contributors)
