# coding: utf8
from __future__ import unicode_literals, division, print_function, absolute_import
import re
import json

from six import PY2
from six.moves import cStringIO as StringIO
from pyramid.renderers import render
from rdflib import Graph, URIRef
import html5lib

from clld.tests.util import TestWithEnv, Route, WithDbAndDataMixin
from clld import RESOURCES
from clld.lib import rdf
from clld.db.models.common import Parameter


_RESOURCES = [_rsc for _rsc in RESOURCES if _rsc.name != 'testresource']


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_detail_html(self):
        self.set_request_properties(matched_route=Route(), map=None)
        for rsc in _RESOURCES:
            if not hasattr(rsc.model, 'first'):
                continue
            res = render(
                '%s/detail_html.mako' % rsc.name,
                dict(ctx=rsc.model.first()),
                request=self.env['request'])
            html5lib.parse(res)

    def test_index_html(self):
        self.set_request_properties(matched_route=Route(), map=None)
        for rsc in _RESOURCES:
            if not hasattr(rsc.model, 'first') or not rsc.with_index:
                continue
            dt = self.env['request'].get_datatable(rsc.name + 's', rsc.model)
            res = render(
                '%s/index_html.mako' % rsc.name,
                dict(ctx=dt),
                request=self.env['request'])
            html5lib.parse(res)

    def test_json(self):
        for rsc in _RESOURCES:
            if not hasattr(rsc.model, 'first'):
                continue
            res = render(
                'json',
                dict(ctx=rsc.model.first()),
                request=self.env['request'])
            json.loads(res)

    def test_rdf(self):
        global RESOURCES
        RESOURCES = _RESOURCES
        qname_as_resource = re.compile('rdf:[a-z]+=\"\w+:\w+\"')
        for rsc in _RESOURCES:
            if not hasattr(rsc.model, 'first'):
                continue
            ctx = rsc.model.first()
            res = render(
                '%s/rdf.mako' % rsc.name, dict(ctx=ctx), request=self.env['request'])
            assert not qname_as_resource.search(res)
            g = Graph()
            g.load(StringIO(res.encode('utf8') if PY2 else res))
            for predicate in ['void:inDataset', 'skos:prefLabel']:
                if predicate == 'void:inDataset' and rsc.name == 'dataset':
                    continue
                subject = URIRef(self.env['request'].resource_url(ctx))
                predicate = URIRef(rdf.url_for_qname(predicate))
                assert (subject, predicate, None) in g
        p = Parameter.get('parameter')
        res = render('parameter/rdf.mako', dict(ctx=p), request=self.env['request'])
        assert p.domain[0].name in res
