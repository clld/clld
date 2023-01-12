from clld.interfaces import IIndex, IRepresentation
from clld.db.models.common import Contribution, Language, Dataset


def test_BibTex(env, env_factory):
    from clld.web.adapters import BibTex

    adapter = BibTex(None)
    assert '@' in adapter.render(Contribution.first(), env['request'])

    res = adapter.render(Dataset.first(), env_factory(zenodo_concept_doi='xyz')['request'])
    assert 'xyz' in res

    env_ = env_factory(zenodo_version_doi='xyz', zenodo_version_tag='v1.0')
    res = adapter.render(Dataset.first(), env_['request'])
    assert 'xyz' in res and 'v1.0' in res


def test_TxtCitation(env):
    from clld.web.adapters import TxtCitation

    adapter = TxtCitation(None)
    assert '.' in adapter.render(Contribution.first(), env['request'])
    assert adapter.label
    adapter.render(Dataset.first(), env['request'])


def test_Json(env):
    from clld.web.adapters.base import Json

    adapter = Json(None)
    adapter.render({'hello': 'world'}, env['request'])


def test_get_adapter(env):
    from clld.web.adapters import get_adapter

    assert get_adapter(IIndex, Language, env['request'], name='text/html') is None


def test_adapter_factory(env):
    from clld.web.adapters.base import adapter_factory

    assert IRepresentation.implementedBy(adapter_factory('template.mako'))
