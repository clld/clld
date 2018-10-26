# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from clld import RESOURCES


def _xml_findall(app, name):
    return list(app.parsed_body.findall('.//%s' % name))


def test_robots(app):
    app.get('/robots.txt')


def test_sitemapindex(app):
    app.get_xml('/sitemap.xml')
    assert len(app.parsed_body.findall(
        '{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')) > 0


def test_sitemap(app):
    app.get_xml('/sitemap.language.0.xml')
    app.get_json('/resourcemap.json?rsc=language')
    app.get_json('/resourcemap.json?rsc=parameter')
    app.get_json('/resourcemap.json?rsc=xxx', status=404)


def test_dataset(app):
    res = app.get_html('/?__admin__=1')
    assert 'notexisting.css' in res
    assert 'notexisting.js' in res
    # Test content negotiation:
    app.get('/', accept='image/png', status=406)
    app.get_xml('/', accept='application/rdf+xml')
    assert app.parsed_body.find(
        './/{http://rdfs.org/ns/void#}Dataset').get(
        '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
    app.get('/void.md.ris')
    assert 'skos:example' in app.get_xml('/void.rdf')


def test_resources(app):
    for rsc in RESOURCES:
        if not rsc.with_index:  # exclude the special case dataset
            continue
        app.get_html('/{0}s/{0}'.format(rsc.name))
        app.get_html('/{0}s/{0}.snippet.html'.format(rsc.name), docroot='div')
        res = app.get_xml('/{0}s/{0}.rdf'.format(rsc.name))
        assert res.headers['Vary'] == 'Accept'
        assert len(_xml_findall(app, '{http://www.w3.org/2004/02/skos/core#}scopeNote')) == 1
        assert len(_xml_findall(app, '{http://www.w3.org/2004/02/skos/core#}altLabel')) > 0
        app.get_html('/%ss' % rsc.name)
        app.get_xml('/%ss.rdf' % rsc.name)
        app.get_json('/{0}s.json'.format(rsc.name))
        assert 'columns' in app.parsed_body
        app.get_dt('/%ss?iDisplayLength=5' % rsc.name)
    app.get_xml('/unitparameters/up2.rdf')
    app.get_html('/combinations/parameter')
    app.get_xml('/combinations/parameter.rdf')


def test_source(app):
    for ext in 'bib en ris mods'.split():
        app.get('/sources/source.' + ext)
        app.get('/sources.' + ext)
    app.get_xml('/sources.rdf?sEcho=1')
    # resources with a name should be listed with rdfs:label in rdf index.
    # see https://github.com/clld/clld/issues/66
    assert len(app.parsed_body.findall(
        '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')) > 0


def test_replacement(app):
    app.get('/languages/replaced', status=301)
    app.get('/languages/gone', status=410)
    app.get('/sources/replaced', status=301)
