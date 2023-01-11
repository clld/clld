import pytest
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotAcceptable, HTTPNotFound, HTTPGone, HTTPFound

from clld.db.models import common
from clld.interfaces import IDataTable

from testutils import XmlResponse


@pytest.mark.parametrize(
    "ctx_cls,model,req_props,content_type",
    [
        (None, common.Contributor, {}, None),
        (None, common.Sentence, {}, None),
        (None, common.Value, {}, None),
        (
            None,
            common.Contributor,
            {'is_xhr': True, 'params': {'sEcho': 'a'}},
            'application/json'),
        (
            None,
            common.Contributor,
            {'is_xhr': True, 'params': {'sEcho': 'a'}},
            'application/json'),
        (
            None,
            common.Contributor,
            {
                'is_xhr': False,
                'matched_route': 'contributors_alt',
                'matchdict': {'ext': 'atom'}},
            None),
    ])
def test_index_view(env, request_factory, ctx_cls, model, req_props, content_type):
    from clld.web.views import index_view

    ctx_cls = ctx_cls or env['registry'].getUtility(IDataTable, name='contributors')

    class X(ctx_cls):
        def row_class(self, item):
            return 'row-%s' % item.pk

    with request_factory(**req_props) as req:
        res = index_view(X(req, model), req)
        assert isinstance(res, Response)
        if content_type:
            assert res.content_type == content_type


def test_resource_view(env, request_factory):
    from clld.web.views import resource_view

    ctx = common.Language(id='a', name='Name')
    res = resource_view(ctx, env['request'])
    assert isinstance(res, Response)

    with request_factory(matchdict={'ext': 'x'}) as req:
        with pytest.raises(HTTPNotAcceptable):
            resource_view(ctx, req)


def test_select_combination(env, request_factory):
    from clld.web.views import select_combination

    with pytest.raises(HTTPNotFound):
        select_combination(None, env['request'])

    with request_factory(params={'parameters': 'parameter'}) as req:
        with pytest.raises(HTTPFound):
            select_combination(None, req)

    with request_factory(
        params=[('parameters', 'parameter'), ('parameters', 'no-domain')]
    ) as req:
        with pytest.raises(HTTPFound):
            select_combination(None, req)


def test__raise(env):
    from clld.web.views import _raise

    with pytest.raises(ValueError):
        _raise(None)


def test__ping(env):
    from clld.web.views import _ping

    assert _ping(None)['status'] == 'ok'


def test_js(env):
    from clld.web.views import js

    js(env['request'])


def test_gone(env):
    from clld.web.views import gone

    with pytest.raises(HTTPGone):
        gone(None, None)


def test_redirect(env):
    from clld.web.views import redirect

    with pytest.raises(HTTPFound):
        redirect(HTTPFound, lambda r: 'x', None, None)


@pytest.mark.parametrize(
    "params,assertion",
    [
        ({}, lambda res: XmlResponse(res).root.tag == 'formats'),
        ({'format': 'bib'}, lambda res: isinstance(res, HTTPNotFound)),
        ({'id': '/contributions/ccc'}, lambda res: isinstance(res, HTTPNotFound)),
        (
            {'id': '/contributions/contribution'},
            lambda res: XmlResponse(res).findall('format')),
        ({'format': 'bib', 'id': '/languages/language'}, lambda res: res),
        ({'format': 'bibtex', 'id': '/contributions/contribution'}, lambda res: res),
    ])
def test_unapi(env, request_factory, params, assertion):
    from clld.web.views import unapi

    with request_factory(params=params) as req:
        assert assertion(unapi(req))
