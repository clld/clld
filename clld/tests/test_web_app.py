import unittest

from pyramid.testing import Configurator
from pyramid.httpexceptions import HTTPNotFound
from mock import Mock
from purl import URL

from clld.db.models.common import Contribution, ValueSet, Language
from clld.tests.util import TestWithEnv, Route


class Tests(TestWithEnv):
    def test_CLLDRequest(self):
        self.assertTrue(isinstance(self.env['request'].purl, URL))
        c = self.env['request'].db.query(Contribution).first()
        self.env['request'].resource_url(c, ext='geojson')

    def test_ctx_factory(self):
        from clld.web.app import ctx_factory

        for model, route in [
            (Contribution, 'contributions'),
            (ValueSet, 'valuesets'),
            (Language, 'languages'),
        ]:
            obj = model.first()
            self.set_request_properties(matchdict={'id': obj.id}, matched_route=Route(route))
            ctx_factory(model, 'index', self.env['request'])
            ctx_factory(model, 'rsc', self.env['request'])

        self.set_request_properties(matchdict={'id': 'xxx'})
        self.assertRaises(HTTPNotFound, ctx_factory, Contribution, 'rsc', self.env['request'])


class Tests2(unittest.TestCase):
    def test_register_app(self):
        from clld.web.app import register_app

        config = Configurator(settings={})
        register_app(config, 'clld')
