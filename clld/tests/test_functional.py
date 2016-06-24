# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from clld.tests.util import TestWithApp, WithDbAndDataMixin
from clld import RESOURCES


class Tests(WithDbAndDataMixin, TestWithApp):
    def _xml_findall(self, name):
        return list(self.app.parsed_body.findall('.//%s' % name))

    def test_robots(self):
        self.app.get('/robots.txt')

    def test_sitemapindex(self):
        self.app.get_xml('/sitemap.xml')
        self.assertTrue(len(self.app.parsed_body.findall(
            '{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')) > 0)

    def test_sitemap(self):
        self.app.get_xml('/sitemap.language.0.xml')
        self.app.get_json('/resourcemap.json?rsc=language')
        self.app.get_json('/resourcemap.json?rsc=parameter')
        self.app.get_json('/resourcemap.json?rsc=xxx', status=404)

    def test_dataset(self):
        res = self.app.get_html('/?__admin__=1')
        assert 'notexisting.css' in res
        assert 'notexisting.js' in res
        self.app.get_xml('/', accept='application/rdf+xml')
        self.app.get('/void.md.ris')
        assert 'skos:example' in self.app.get_xml('/void.rdf')

    def test_resources(self):
        for rsc in RESOURCES:
            if not rsc.with_index:  # exclude the special case dataset
                continue
            self.app.get_html('/{0}s/{0}'.format(rsc.name))
            self.app.get_html('/{0}s/{0}.snippet.html'.format(rsc.name), docroot='div')
            self.app.get_xml('/{0}s/{0}.rdf'.format(rsc.name))
            self.assertEquals(
                len(self._xml_findall('{http://www.w3.org/2004/02/skos/core#}scopeNote')),
                1)
            self.assertGreater(
                len(self._xml_findall('{http://www.w3.org/2004/02/skos/core#}altLabel')),
                0)
            self.app.get_html('/%ss' % rsc.name)
            self.app.get_xml('/%ss.rdf' % rsc.name)
            self.app.get_json('/{0}s.json'.format(rsc.name))
            self.assertIn('columns', self.app.parsed_body)
            self.app.get_dt('/%ss?iDisplayLength=5' % rsc.name)
        self.app.get_xml('/unitparameters/up2.rdf')
        self.app.get_html('/combinations/parameter')

    def test_source(self):
        for ext in 'bib en ris mods'.split():
            self.app.get('/sources/source.' + ext)
            self.app.get('/sources.' + ext)
        self.app.get_xml('/sources.rdf?sEcho=1')
        # resources with a name should be listed with rdfs:label in rdf index.
        # see https://github.com/clld/clld/issues/66
        self.assertTrue(len(self.app.parsed_body.findall(
            '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')) > 0)

    def test_replacement(self):
        self.app.get('/languages/replaced', status=301)
        self.app.get('/languages/gone', status=410)
        self.app.get('/sources/replaced', status=301)
