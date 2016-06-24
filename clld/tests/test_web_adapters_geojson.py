# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import
import json

from mock import Mock

from clld.db.models.common import Parameter, Language
from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.web.adapters import geojson
from clld.web.datatables.base import DataTable

geojson.pacific_centered()


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_GeoJson(self):
        adapter = geojson.GeoJson(None)
        self.assertEquals(len(list(adapter.feature_iterator(None, None))), 0)
        self.assertEquals(len(list(adapter.feature_iterator(Language(), None))), 1)
        self.assertEquals(
            len(list(adapter.feature_iterator(Mock(languages=[Language()]), None))), 1)

    def test_GeoJsonParameter(self):
        adapter = geojson.GeoJsonParameter(None)
        self.assertTrue(
            '{' in adapter.render(Parameter.get('no-domain'), self.env['request']))

        self.set_request_properties(params=dict(domainelement='de'))
        res = json.loads(adapter.render(Parameter.get('parameter'), self.env['request']))
        self.assertTrue(len(res['features']) > 0)
        self.assertIn('label', res['features'][0]['properties'])

    def test_GeoJsonParameterMultipleValueSets(self):
        adapter = geojson.GeoJsonParameterMultipleValueSets(None)
        self.assertTrue(
            '{' in adapter.render(Parameter.get('no-domain'), self.env['request']))

    def test_GeoJsonParameterFlatProperties(self):
        adapter = geojson.GeoJsonParameterFlatProperties(None)
        self.assertTrue(
            '{' in adapter.render(Parameter.get('no-domain'), self.env['request']))

    def test_GeoJsonLanguages(self):
        class MockLanguages(DataTable):
            def get_query(self, *args, **kw):
                return [Language.first()]

        adapter = geojson.GeoJsonLanguages(None)
        self.assertIn(
            'Point',
            adapter.render(
                MockLanguages(self.env['request'], Language), self.env['request']))

    def test_get_lonlat(self):
        self.assertIsNone(geojson.get_lonlat(None))
        self.assertIsNone(geojson.get_lonlat((None, 5)))
        self.assertGreater(geojson.get_lonlat((-50, 1))[0], 0)
        self.assertAlmostEquals(geojson.get_lonlat(Mock(latitude=1, longitude=1)), (1, 1))

    def test_get_feature(self):
        l = Language.first()
        self.assertEquals(geojson.get_feature(l)['id'], l.id)
        self.assertEquals(geojson.get_feature(l)['properties']['name'], l.name)
        self.assertEquals(geojson.get_feature(l, name='geo')['properties']['name'], 'geo')
