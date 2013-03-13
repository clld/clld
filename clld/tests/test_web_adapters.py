import unittest

from pyramid.testing import Configurator
from pyramid.httpexceptions import HTTPNotFound
from mock import Mock

from clld.interfaces import IIndex
from clld.db.models.common import Contribution, Parameter, Language
from clld.lib.purl import URL
from clld.tests.util import TestWithEnv, Route


class Tests(TestWithEnv):
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

    def test_GeoJsonParameter(self):
        from clld.web.adapters import GeoJsonParameter

        adapter = GeoJsonParameter(None)
        self.assertTrue(
            '{' in adapter.render(Parameter.get('no-domain'), self.env['request']))

        self.set_request_properties(params=dict(domainelement='de'))
        self.assertTrue(
            '{' in adapter.render(Parameter.get('p'), self.env['request']))

    def test_GeoJsonLanguages(self):
        from clld.web.adapters import GeoJsonLanguages

        class MockLanguages(Mock):
            def get_query(self, *args, **kw):
                return [Language.first()]

        adapter = GeoJsonLanguages(None)
        self.assertTrue(
            '{' in adapter.render(MockLanguages(), self.env['request']))

    def test_get_adapter(self):
        from clld.web.adapters import get_adapter

        self.assertEqual(
            None, get_adapter(IIndex, Language, self.env['request'], name='text/html'))


class Tests2(unittest.TestCase):
    def test_register_app(self):
        pass
