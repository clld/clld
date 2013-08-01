import unittest

from mock import Mock, patch


class Tests(unittest.TestCase):
    def test_properties_as_xml_snippet(self):
        from clld.lib.rdf import properties_as_xml_snippet

        properties_as_xml_snippet('subject', [('foaf:name', 'a name')])
