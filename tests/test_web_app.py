# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import
import importlib

import pytest
from zope.interface import Interface
from pyramid.testing import Configurator
from pyramid.httpexceptions import HTTPNotFound
from purl import URL

from clld.db.models.common import Contribution, ValueSet, Language, Language_files
from clld.interfaces import IMapMarker
from clld.web.adapters.download import N3Dump


def test_CLLDRequest(env):
    assert isinstance(env['request'].purl, URL)
    c = env['request'].db.query(Contribution).first()
    env['request'].resource_url(c, ext='geojson')
    assert env['request'].ctx_for_url('/some/path/to/nowhere') is None
    assert env['request'].ctx_for_url('/')
    env['request'].file_url(Language_files(id='1', object=Language.first()))
    assert env['request'].get_datatable('valuesets', ValueSet)
    assert env['request'].blog is None


def test_menu_item(env):
    from clld.web.app import menu_item

    assert menu_item('contributions', None, env['request'])


def test_ctx_factory(request_factory):
    from clld.web.app import ctx_factory

    for model, route in [
        (Contribution, 'contributions'),
        (ValueSet, 'valuesets'),
        (Language, 'languages'),
    ]:
        obj = model.first()

        with request_factory(matchdict={'id': obj.id}, matched_route=route) as req:
            ctx_factory(model, 'index', req)
            ctx_factory(model, 'rsc', req)

    with request_factory(matchdict={'id': 'xxx'}) as req:
        with pytest.raises(HTTPNotFound):
            ctx_factory(Contribution, 'rsc', req)


def test_MapMarker(env):
    marker = env['request'].registry.getUtility(IMapMarker)
    assert marker(None, env['request'])


def test_add_config_from_file(testsdir):
    from clld.web.app import add_settings_from_file

    config = Configurator()
    add_settings_from_file(config, testsdir / 'test.ini')
    assert 'app:main.use' in config.registry.settings


def test_config():
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


def test_includeme_error(tmpdir, capsys):
    import sys
    sys.path.append(str(tmpdir))
    pkg = tmpdir.join('failingapp')
    pkg.mkdir()
    pkg.join('__init__.py').write_text('#\n', 'ascii')
    pkg.join('util.py').write_text('import xyzxyz', 'ascii')
    config = Configurator(
        root_package=importlib.import_module('failingapp'),
        settings={'sqlalchemy.url': 'sqlite://'})
    with pytest.raises(ImportError):
        config.include('clld.web.app')
    out, err = capsys.readouterr()
    assert 'failingapp.util' in out
    sys.path.pop()
