import unittest


class Tests(unittest.TestCase):
    def test_properties_as_xml_snippet(self):
        from clld.lib.rdf import properties_as_xml_snippet

        properties_as_xml_snippet(
            'subject', [('foaf:name', 'a name'), ('foaf:homepage', 'http://example.org')])

    def test_convert(self):
        from clld.lib.rdf import ClldGraph, convert, FORMATS

        g = ClldGraph()
        for from_ in FORMATS:
            for to_ in FORMATS:
                convert(g.serialize(format=from_), from_, to_)
