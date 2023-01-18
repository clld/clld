import warnings
import importlib

import pytest
from zope.interface import Interface
from pyramid.testing import Configurator
from pyramid.httpexceptions import HTTPNotFound

from clld.db.models.common import Contribution, ValueSet, Language, Language_files
from clld.interfaces import IMapMarker, IDataTable
from clld.web.adapters.download import N3Dump


@pytest.fixture
def config():
    with warnings.catch_warnings():
        warnings.filterwarnings(
            'ignore', category=DeprecationWarning, module='importlib._bootstrap')

        config_ = Configurator(
            root_package=importlib.import_module('clld.web'),
            settings={
                'sqlalchemy.url': 'sqlite://',
                'clld.pacific_centered_maps': True})
        config_.include('clld.web.app')
        return config_


def test_CLLDRequest(env):
    c = env['request'].db.query(Contribution).first()
    env['request'].resource_url(c, ext='geojson')
    assert env['request'].ctx_for_url('/some/path/to/nowhere') is None
    assert env['request'].ctx_for_url('/')
    env['request'].file_url(Language_files(id='1', object=Language.first()))
    assert env['request'].get_datatable('valuesets', ValueSet)
    assert env['request'].contact_email_address.startswith('from.settings')


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


def test_config(config):
    class IF(Interface):
        pass

    # should have no effect, because a resource with this name is registered by
    # default:
    config.register_menu('languages', ('sources', dict(label='References')))
    config.register_resource('language', None, None)
    config.register_resource('testresource', Language, IF, with_index=True, test=True)
    config.register_download(N3Dump(Language, 'clld'))
    config.add_301('/301pattern', 'http://example.org')
    config.add_410('/410pattern')


def test_no_overwrite_registration(config):
    config.register_utility(1, IMapMarker)
    assert config.registry.queryUtility(IMapMarker) == 1
    config.register_utility(2, IMapMarker)
    assert config.registry.queryUtility(IMapMarker) == 2
    config.register_utility(3, IMapMarker, overwrite=False)
    assert config.registry.queryUtility(IMapMarker) == 2

    config.register_datatable('route', 1)
    assert config.registry.queryUtility(IDataTable, name='route') == 1
    config.register_datatable('route', 2, overwrite=False)
    assert config.registry.queryUtility(IDataTable, name='route') == 1


def test_includeme_error(tmp_path, capsys):
    import sys
    sys.path.append(str(tmp_path))
    pkg = tmp_path.joinpath('failingapp')
    pkg.mkdir()
    pkg.joinpath('__init__.py').write_text('#\n', 'ascii')
    pkg.joinpath('util.py').write_text('import xyzxyz', 'ascii')
    config = Configurator(
        root_package=importlib.import_module('failingapp'),
        settings={'sqlalchemy.url': 'sqlite://'})
    with pytest.raises(ImportError):
        config.include('clld.web.app')
    out, err = capsys.readouterr()
    assert 'failingapp.util' in out
    sys.path.pop()
