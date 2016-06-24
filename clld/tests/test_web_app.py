# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import
import importlib

from zope.interface import Interface
from pyramid.testing import Configurator
from pyramid.httpexceptions import HTTPNotFound
from purl import URL

from clld.db.models.common import Contribution, ValueSet, Language, Language_files
from clld.tests.util import TestWithEnv, Route, TESTS_DIR, WithDbAndDataMixin
from clld.interfaces import IMapMarker
from clld.web.adapters.download import N3Dump


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_CLLDRequest(self):
        self.assertTrue(isinstance(self.env['request'].purl, URL))
        c = self.env['request'].db.query(Contribution).first()
        self.env['request'].resource_url(c, ext='geojson')
        self.assertEqual(None, self.env['request'].ctx_for_url('/some/path/to/nowhere'))
        assert self.env['request'].ctx_for_url('/')
        self.env['request'].file_url(Language_files(id='1', object=Language.first()))
        assert self.env['request'].get_datatable('valuesets', ValueSet)
        assert self.env['request'].blog is None

    def test_menu_item(self):
        from clld.web.app import menu_item

        assert menu_item('contributions', None, self.env['request'])

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

    def test_config(self):
        class IF(Interface):
            pass

        config = Configurator(
            root_package=importlib.import_module('clld.web'),
            settings={
                'sqlalchemy.url': 'sqlite://',
                'clld.pacific_centered_maps': True})
        config.include('clld.web.app')
        # should have no effect, because a resource with this name is registered by
        # default:
        config.register_menu('languages', ('sources', dict(label='References')))
        config.register_resource('language', None, None)
        config.register_resource('testresource', Language, IF, with_index=True, test=True)
        config.register_download(N3Dump(Language, 'clld'))
        config.add_301('/301pattern', 'http://example.org')
        config.add_410('/410pattern')
