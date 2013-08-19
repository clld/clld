import unittest

from pyramid.testing import Configurator
from pyramid.httpexceptions import HTTPNotFound
from purl import URL

from clld.db.models.common import Contribution, ValueSet, Language, Language_files
from clld.tests.util import TestWithEnv, Route, TESTS_DIR
from clld.interfaces import IMapMarker


class Tests(TestWithEnv):
    def test_CLLDRequest(self):
        self.assertTrue(isinstance(self.env['request'].purl, URL))
        c = self.env['request'].db.query(Contribution).first()
        self.env['request'].resource_url(c, ext='geojson')
        self.assertEqual(None, self.env['request'].ctx_for_url('/some/path/to/nowhere'))
        self.env['request'].file_url(Language_files(id='1', object=Language.first()))

    def test_ctx_factory(self):
        from clld.web.app import ctx_factory

        for model, route in [
            (Contribution, 'contributions'),
            (ValueSet, 'valuesets'),
            (Language, 'languages'),
        ]:
            obj = model.first()
            self.set_request_properties(
                matchdict={'id': obj.id}, matched_route=Route(route))
            ctx_factory(model, 'index', self.env['request'])
            ctx_factory(model, 'rsc', self.env['request'])

        self.set_request_properties(matchdict={'id': 'xxx'})
        self.assertRaises(
            HTTPNotFound, ctx_factory, Contribution, 'rsc', self.env['request'])

    def test_MapMarker(self):
        marker = self.env['request'].registry.getUtility(IMapMarker)
        self.assertTrue(marker(None, self.env['request']))

    def test_add_config_from_file(self):
        from clld.web.app import add_settings_from_file

        config = Configurator()
        add_settings_from_file(config, TESTS_DIR.joinpath('test.ini'))
        assert 'app:main.use' in config.registry.settings
