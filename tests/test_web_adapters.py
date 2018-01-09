# coding: utf8
from __future__ import unicode_literals
from clld.interfaces import IIndex, IRepresentation
from clld.db.models.common import Contribution, Language, Dataset


def test_BibTex(env):
    from clld.web.adapters import BibTex

    adapter = BibTex(None)
    assert '@' in adapter.render(Contribution.first(), env['request'])


def test_TxtCitation(env):
    from clld.web.adapters import TxtCitation

    adapter = TxtCitation(None)
    assert '.' in adapter.render(Contribution.first(), env['request'])
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
