import json

import pytest

from clld.db.models.common import Parameter, Language
from clld.web.adapters import geojson
from clld.web.datatables.base import DataTable

geojson.pacific_centered()


def test_GeoJson(mocker):
    adapter = geojson.GeoJson(None)
    assert len(list(adapter.feature_iterator(None, None))) == 0
    assert len(list(adapter.feature_iterator(Language(), None))) == 1
    assert len(list(adapter.feature_iterator(mocker.Mock(languages=[Language()]), None))) == 1


def test_GeoJsonParameter(env, request_factory):
    adapter = geojson.GeoJsonParameter(None)
    assert '{' in adapter.render(Parameter.get('no-domain'), env['request'])

    with request_factory(params=dict(domainelement='de')) as req:
        res = json.loads(adapter.render(Parameter.get('parameter'), req))
        assert len(res['features']) > 0
        assert 'label' in res['features'][0]['properties']


def test_GeoJsonParameterMultipleValueSets(env):
    adapter = geojson.GeoJsonParameterMultipleValueSets(None)
    assert '{' in adapter.render(Parameter.get('no-domain'), env['request'])


def test_GeoJsonParameterFlatProperties(env):
    adapter = geojson.GeoJsonParameterFlatProperties(None)
    assert '{' in adapter.render(Parameter.get('no-domain'), env['request'])


def test_GeoJsonLanguages(env):
    class MockLanguages(DataTable):
        def get_query(self, *args, **kw):
            return [Language.first()]

    adapter = geojson.GeoJsonLanguages(None)
    assert 'Point' in\
        adapter.render(
            MockLanguages(env['request'], Language), env['request'])


def test_get_lonlat(mocker):
    assert geojson.get_lonlat(None) is None
    assert geojson.get_lonlat((None, 5)) is None
    assert geojson.get_lonlat((-50, 1))[0] > 0
    assert geojson.get_lonlat(mocker.Mock(latitude=1, longitude=1)) == (pytest.approx(1), pytest.approx(1))


def test_get_feature(data):
    l = Language.first()
    assert geojson.get_feature(l)['id'] == l.id
    assert geojson.get_feature(l)['properties']['name'] == l.name
    assert geojson.get_feature(l, name='geo')['properties']['name'] == 'geo'
