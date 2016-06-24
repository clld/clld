# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from clldutils.path import Path
from clldutils.testing import WithTempDir

from clld.tests.util import WithCustomLanguageMixin, WithDbMixin, WithDbAndDataMixin
from clld.db.meta import DBSession


class Tests(WithCustomLanguageMixin, WithDbMixin, WithTempDir):
    def test_Config(self):
        from clld.db.models.common import Config

        self.assertEquals(Config.replacement_key('X', 'Y'), '__X_Y__')
        self.assertEquals(Config.replacement_key(None, 'Y'), '__NoneType_Y__')

    def test_Files(self):
        from clld.db.models.common import Sentence, Sentence_files

        l = Sentence(id='abc', name='Name')
        f = Sentence_files(object=l, id='abstract', mime_type='audio/mpeg')
        p = f.create(self.tmp_path('clldtest'), 'content')
        assert Path(p).exists()

        l._files.append(f)
        DBSession.add(l)
        DBSession.flush()
        DBSession.refresh(l)
        assert l.files
        assert l.audio

    def test_Dataset(self):
        from clld import RESOURCES
        from clld.db.models.common import Dataset, Source

        d = Dataset(id='abc', domain='test')
        DBSession.add(d)
        DBSession.flush()
        self.assertEquals(d.jsondata, d.jsondatadict)
        d.get_stats(RESOURCES, source=Source.id == None)

    def test_Contributor(self):
        from clld.db.models.common import Contributor

        d = Contributor(id='abc')
        d.last_first()
        d = Contributor(id='abc', name='Robert Forkel')
        self.assertTrue(d.last_first().startswith('Forkel'))

    def test_Language(self):
        from clld.db.models.common import Language

        d = Language(id='abc')
        assert d.glottocode is None
        assert d.iso_code is None
        assert d.__solr__(None)

    def test_Source(self):
        from clld.db.models.common import Source

        d = Source(id='abc')
        self.assertIsNone(d.gbs_identifier)
        d = Source(id='abc', jsondata={'gbs': {'volumeInfo': {}}})
        self.assertIsNone(d.gbs_identifier)
        d = Source(
            id='abc',
            jsondata={
                'gbs': {
                    'volumeInfo': {
                        'industryIdentifiers': [{'type': 'x', 'identifier': 'y'}]}}})
        self.assertEquals(d.gbs_identifier, 'y')
        d = Source(
            id='abc',
            jsondata={
                'gbs': {
                    'volumeInfo': {
                        'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': ''}]}}})
        self.assertEquals(d.gbs_identifier, 'ISBN:')
        d = Source(
            id='abc',
            jsondata={
                'gbs': {
                    'volumeInfo': {
                        'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': ''}]}}})
        self.assertEquals(d.gbs_identifier, 'ISBN:')
        d.bibtex()

    def test_Data(self):
        from clld.db.models.common import Language, Language_data

        l = Language(id='abc', name='Name')
        l.data.append(Language_data(key='abstract', value='c'))
        DBSession.add(l)
        DBSession.flush()
        DBSession.refresh(l)
        self.assertEqual(l.datadict()['abstract'], 'c')

    def test_Unit(self):
        from clld.db.models.common import Unit, Language

        u = Unit(name='unit', language=Language(name='language'))
        assert u.__solr__(None)

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

    def test_Identifier(self):
        from clld.db.models.common import Identifier, IdentifierType

        i = Identifier(id='a', name='a', type=IdentifierType.iso.value)
        assert i.url()
        i = Identifier(id='a', name='a', type='xxx')
        assert i.url() is None


class MoreTests(WithCustomLanguageMixin, WithDbAndDataMixin, WithTempDir):
    def test_Contribution(self):
        from clld.db.models.common import Contribution

        c = DBSession.query(Contribution).first()
        assert c.formatted_contributors()

    def test_Value(self):
        from clld.db.models.common import Value

        self.assertTrue('valueset' in Value.first().__json__(None))

    def test_Sentence(self):
        from clld.db.models.common import Sentence

        self.assertTrue('language_t' in Sentence.first().__solr__(None))

    def test_Combination(self):
        from clld.db.models.common import Combination, Parameter

        p = Parameter.first()
        c = Combination.get(Combination.delimiter.join(2 * [p.id]))
        assert c.values
        assert c.domain
