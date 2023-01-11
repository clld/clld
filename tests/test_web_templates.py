import re
import json
import io

import pytest

from pyramid.renderers import render
from rdflib import Graph, URIRef
import html5lib

from clld import RESOURCES
from clld.lib import rdf
from clld.db.models.common import Parameter


_RESOURCES = [_rsc for _rsc in RESOURCES if _rsc.name != 'testresource']


@pytest.mark.parametrize(
    'rsc',
    [r for r in _RESOURCES if hasattr(r.model, 'first')],
)
def test_detail_html(request_factory, rsc):
    with request_factory(matched_route='home', map=None) as req:
        res = render(
            '%s/detail_html.mako' % rsc.name, {'ctx': rsc.model.first()}, request=req)
        html5lib.parse(res)
        if rsc.name == 'dataset':
            assert 'http://example.org/privacy' in res
            assert 'Privacy Policy' in res


@pytest.mark.parametrize(
    'rsc',
    [r for r in _RESOURCES if hasattr(r.model, 'first') and r.name != 'dataset'],
)
def test_index_html(request_factory, rsc):
    with request_factory(matched_route='home', map=None) as req:
        dt = req.get_datatable(rsc.name + 's', rsc.model)
        res = render('%s/index_html.mako' % rsc.name, {'ctx': dt}, request=req)
        html5lib.parse(res)


@pytest.mark.parametrize(
    'rsc',
    [r for r in _RESOURCES if hasattr(r.model, 'first')],
)
def test_json(env, rsc):
    res = render('json', dict(ctx=rsc.model.first()), request=env['request'])
    json.loads(res)


def test_rdf(env):
    global RESOURCES
    RESOURCES = _RESOURCES
    qname_as_resource = re.compile(r'rdf:[a-z]+=\"\w+:\w+\"')
    for rsc in _RESOURCES:
        if not hasattr(rsc.model, 'first'):
            continue
        ctx = rsc.model.first()
        res = render('%s/rdf.mako' % rsc.name, dict(ctx=ctx), request=env['request'])
        assert not qname_as_resource.search(res)
        g = Graph()
        g.parse(io.StringIO(res), format='xml')
        for predicate in ['void:inDataset', 'skos:prefLabel']:
            if predicate == 'void:inDataset' and rsc.name == 'dataset':
                continue
            subject = URIRef(env['request'].resource_url(ctx))
            predicate = URIRef(rdf.url_for_qname(predicate))
            assert (subject, predicate, None) in g
    p = Parameter.get('parameter')
    res = render('parameter/rdf.mako', dict(ctx=p), request=env['request'])
    assert p.domain[0].name in res
