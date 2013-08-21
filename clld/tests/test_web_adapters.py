import os
import unittest
from tempfile import mktemp

from mock import Mock

from clld.interfaces import IIndex, IRepresentation
from clld.db.models.common import Contribution, Parameter, Language, Dataset, Source
from clld.tests.util import TestWithEnv


class Tests(TestWithEnv):
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

    def test_get_adapter(self):
        from clld.web.adapters import get_adapter

        self.assertEqual(
            None, get_adapter(IIndex, Language, self.env['request'], name='text/html'))

    def test_adapter_factory(self):
        from clld.web.adapters.base import adapter_factory

        assert IRepresentation.implementedBy(adapter_factory('template.mako'))


class Tests2(unittest.TestCase):
    def test_register_app(self):
        pass
