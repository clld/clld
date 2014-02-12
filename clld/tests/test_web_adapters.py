import os
import unittest
from tempfile import mktemp

from mock import Mock, MagicMock, patch

from clld.interfaces import IIndex, IRepresentation
from clld.db.models.common import Contribution, Parameter, Language, Dataset, Source
from clld.tests.util import TestWithEnv


class Tests(TestWithEnv):
    def test_download_dir(self):
        from clld.web.adapters.download import download_dir

        assert download_dir('clld')

    def testDownload(self):
        from clld.web.adapters.download import Download

        class TestDownload(Download):
            _path = mktemp()

            def asset_spec(self, req):
                return self._path

        dl = TestDownload(Source, 'clld', ext='bib')
        abspath = dl.abspath(self.env['request'])
        assert not os.path.exists(abspath)
        dl.create(self.env['request'], verbose=False)
        dl.size(self.env['request'])
        dl.label(self.env['request'])
        assert os.path.exists(abspath)
        os.remove(abspath)

        dl = TestDownload(Source, 'clld', ext='rdf')
        dl.create(self.env['request'], verbose=False)
        os.remove(dl.abspath(self.env['request']))

    def testDownload_url(self):
        from clld.web.adapters.download import Download

        with patch.multiple(
                'clld.web.adapters.download',
                download_asset_spec=Mock(
                    return_value='clld:web/static/images/favicon.ico')):
            dl = Download(Source, 'clld', ext='bib')
            assert dl.url(self.env['request'])

    def testDownload2(self):
        from clld.web.adapters.download import CsvDump, N3Dump, RdfXmlDump

        with patch.multiple(
            'clld.web.adapters.download',
            GzipFile=MagicMock(),
            ZipFile=MagicMock(),
            path=Mock(return_value=Mock(
                dirname=Mock(return_value=Mock(exists=Mock(return_value=False))))),
        ):
            dl = CsvDump(Language, 'clld')
            dl.create(self.env['request'], verbose=False)
            dl.create(self.env['request'], filename='name.n3', verbose=False)
            dl = N3Dump(Language, 'clld')
            dl.create(self.env['request'], verbose=False)
            dl = RdfXmlDump(Language, 'clld')
            dl.create(self.env['request'], verbose=False)

    def test_BibTex(self):
        from clld.web.adapters import BibTex

        adapter = BibTex(None)
        self.assertTrue(
            '@' in adapter.render(Contribution.first(), self.env['request']))

    def test_TxtCitation(self):
        from clld.web.adapters import TxtCitation

        adapter = TxtCitation(None)
        self.assertTrue(
            '.' in adapter.render(Contribution.first(), self.env['request']))
        adapter.render(Dataset.first(), self.env['request'])

    def test_GeoJsonParameter(self):
        from clld.web.adapters import GeoJsonParameter

        adapter = GeoJsonParameter(None)
        self.assertTrue(
            '{' in adapter.render(Parameter.get('no-domain'), self.env['request']))

        self.set_request_properties(params=dict(domainelement='de'))
        self.assertTrue(
            '{' in adapter.render(Parameter.get('parameter'), self.env['request']))

    def test_GeoJsonParameterFlatProperties(self):
        from clld.web.adapters import GeoJsonParameterFlatProperties

        adapter = GeoJsonParameterFlatProperties(None)
        self.assertTrue(
            '{' in adapter.render(Parameter.get('no-domain'), self.env['request']))

    def test_GeoJsonLanguages(self):
        from clld.web.adapters import GeoJsonLanguages

        class MockLanguages(Mock):
            def get_query(self, *args, **kw):
                return [Language.first()]

        adapter = GeoJsonLanguages(None)
        self.assertTrue(
            '{' in adapter.render(MockLanguages(), self.env['request']))

    def test_Json(self):
        from clld.web.adapters.base import Json

        adapter = Json(None)
        adapter.render({'hello': 'world'}, self.env['request'])

    def test_SolrDoc(self):
        from clld.web.adapters.base import SolrDoc

        adapter = SolrDoc(None)
        adapter.render(Language.first(), self.env['request'])

    def test_get_adapter(self):
        from clld.web.adapters import get_adapter

        self.assertEqual(
            None, get_adapter(IIndex, Language, self.env['request'], name='text/html'))

    def test_adapter_factory(self):
        from clld.web.adapters.base import adapter_factory

        assert IRepresentation.implementedBy(adapter_factory('template.mako'))


class Tests2(unittest.TestCase):
    def test_pacific_centered(self):
        from clld.web.adapters.geojson import pacific_centered_coordinates

        assert pacific_centered_coordinates(Mock(longitude=-50, latitude=1))[0] > 0

    def test_register_app(self):
        pass
