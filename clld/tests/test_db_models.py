from __future__ import unicode_literals

from six import PY3

from clld.tests.util import TestWithDb, TestWithDbAndData
from clld.db.meta import DBSession


class Tests(TestWithDb):
    def test_Files(self):
        from clld.db.models.common import Language, Language_files, File

        if PY3:
            return  # pragma: no cover

        l = Language(id='abc', name='Name')
        assert l.iso_code is None
        l.files.append(Language_files(name='abstract', file=File(content='c')))
        DBSession.add(l)
        DBSession.flush()
        DBSession.refresh(l)
        f = l.filesdict()['abstract']
        self.assertEqual(f.content, 'c')
        self.assertEqual(f.id, f.pk)
        self.assertTrue(f.data_uri().startswith('data:'))

    def test_Dataset(self):
        from clld import RESOURCES
        from clld.db.models.common import Dataset, Source

        d = Dataset(id='abc', domain='test')
        DBSession.add(d)
        DBSession.flush()
        d.get_stats(RESOURCES, source=Source.id == None)

    def test_Contributor(self):
        from clld.db.models.common import Contributor

        d = Contributor(id='abc')
        d.last_first()
        d = Contributor(id='abc', name='Robert Forkel')
        self.assertTrue(d.last_first().startswith('Forkel'))

    def test_Source(self):
        from clld.db.models.common import Source

        d = Source(id='abc')
        d.gbs_identifier
        d = Source(id='abc', jsondata={'gbs': {'volumeInfo': {}}})
        d.gbs_identifier
        d = Source(
            id='abc',
            jsondata={
                'gbs': {
                    'volumeInfo': {
                        'industryIdentifiers': [{'type': 'x', 'identifier': 'y'}]}}})
        d.gbs_identifier
        d = Source(
            id='abc',
            jsondata={
                'gbs': {
                    'volumeInfo': {
                        'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': ''}]}}})
        d.gbs_identifier
        d = Source(
            id='abc',
            jsondata={
                'gbs': {
                    'volumeInfo': {
                        'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': ''}]}}})
        d.gbs_identifier
        d.bibtex()

    def test_Data(self):
        from clld.db.models.common import Language, Language_data

        l = Language(id='abc', name='Name')
        l.data.append(Language_data(key='abstract', value='c'))
        DBSession.add(l)
        DBSession.flush()
        DBSession.refresh(l)
        self.assertEqual(l.datadict()['abstract'], 'c')

    def test_UnitValue(self):
        from clld.db.models.common import UnitParameter, UnitValue, UnitDomainElement

        p1 = UnitParameter()
        p2 = UnitParameter()
        v = UnitValue(
            unitdomainelement=UnitDomainElement(parameter=p1, name='ude'))
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
        from clld.db.models.common import Contribution

        c = DBSession.query(Contribution).first()
        self.assertTrue(c.primary_contributors)
        self.assertTrue(c.secondary_contributors)

    def test_Value(self):
        from clld.db.models.common import Value

        self.assertTrue('valueset' in Value.first().__json__(None))
