from __future__ import unicode_literals, division, absolute_import, print_function
import unittest


class Tests(unittest.TestCase):
    def test_properties_as_xml_snippet(self):
        from clld.lib.rdf import properties_as_xml_snippet

        properties_as_xml_snippet(
            'subject', [('foaf:name', 'a name'), ('foaf:homepage', 'http://example.org')])

        p = properties_as_xml_snippet(
            'http://example.org', [('dcterms:title', 'ttt')])
        assert 'ttt' in p

    def test_convert(self):
        from clld.lib.rdf import ClldGraph, convert, FORMATS

        g = ClldGraph()
        for from_ in FORMATS:
            for to_ in list(FORMATS.keys()) + [None]:
                convert(g.serialize(format=from_), from_, to_)
