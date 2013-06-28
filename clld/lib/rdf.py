"""
This module provides functionality for handling our data as rdf.
"""
from cStringIO import StringIO

from rdflib import Graph

from clld.util import encoded


FORMATS = {
    'xml': 'application/rdf+xml',
    'n3': 'text/n3',
    'nt': 'text/nt',
}


def convert(string, from_, to_):
    assert from_ in FORMATS and to_ in FORMATS
    g = Graph()
    g.parse(StringIO(encoded(string)), format=from_)
    out = StringIO()
    g.serialize(out, format=to_)
    out.seek(0)
    return out.read()
