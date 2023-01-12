import pytest

from clld import RESOURCES


def _xml_findall(app, name):
    return list(app.parsed_body.findall('.//%s' % name))


def test_robots(app):
    res = app.get('/robots.txt')
    assert 'User-agent: robot1\nDisallow: /\n' in res.body.decode('utf8')


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
    _ = app.get('/void.md.bib')
    res = app.get_html('/?__admin__=1')
    assert 'notexisting.css' in res
    assert 'notexisting.js' in res
    # Test content negotiation:
    app.get('/', accept='image/png', status=406)
    app.get_xml('/', accept='application/rdf+xml')
    assert app.parsed_body.find(
        './/{http://rdfs.org/ns/void#}Dataset').get(
        '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
    assert 'skos:example' in app.get_xml('/void.rdf')
    # Test __locale__ param is propagated:
    res = app.get_html('/?__locale__=en')
    assert '?__locale__=en' in res


@pytest.mark.parametrize('rsc', [rsc for rsc in RESOURCES if rsc.with_index])
def test_resources(app, rsc):
    app.get_html('/{0}s/{0}'.format(rsc.name))
    app.get_html('/{0}s/{0}.snippet.html'.format(rsc.name), docroot='div')
    res = app.get_xml('/{0}s/{0}.rdf'.format(rsc.name))
    assert res.headers['Vary'] == 'Accept'
    assert len(_xml_findall(app, '{http://www.w3.org/2004/02/skos/core#}scopeNote')) == 1
    assert len(_xml_findall(app, '{http://www.w3.org/2004/02/skos/core#}altLabel')) > 0
    app.get_html('/%ss' % rsc.name)
    app.get_xml('/%ss.rdf' % rsc.name)
    app.get_dt('/%ss?iDisplayLength=5' % rsc.name)


def test_resources_special_cases(app):
    app.get_xml('/unitparameters/up2.rdf')
    app.get_html('/combinations/parameter')
    app.get_xml('/combinations/parameter.rdf')


def test_source(app):
    app.get('/sources/source.bib')
    app.get('/sources.bib')
    app.get_xml('/sources.rdf?sEcho=1')
    # resources with a name should be listed with rdfs:label in rdf index.
    # see https://github.com/clld/clld/issues/66
    assert len(app.parsed_body.findall(
        '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')) > 0


@pytest.mark.parametrize(
    'route,status',
    [('/languages/replaced', 301), ('/languages/gone', 410), ('/sources/replaced', 301)]
)
def test_replacement(app, route, status):
    app.get(route, status=status)
