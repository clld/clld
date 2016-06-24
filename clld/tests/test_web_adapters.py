# coding: utf8
from __future__ import unicode_literals
from clld.interfaces import IIndex, IRepresentation
from clld.db.models.common import Contribution, Language, Dataset
from clld.tests.util import TestWithEnv, WithDbAndDataMixin


class Tests(WithDbAndDataMixin, TestWithEnv):
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
