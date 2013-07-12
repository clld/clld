"""
This module provides functionality for handling our data as rdf.
"""
from collections import namedtuple
from cStringIO import StringIO

from rdflib import Graph

from clld.util import encoded


Notation = namedtuple('Notation', 'name extension mimetype uri')

FORMATS = dict((n.name, n) for n in [
    Notation('xml', 'rdf', 'application/rdf+xml', 'http://www.w3.org/ns/formats/RDF_XML'),
    Notation('n3', 'n3', 'text/n3', 'http://www.w3.org/ns/formats/N3'),
    Notation('nt', 'nt', 'text/nt', 'http://www.w3.org/ns/formats/N-Triples'),
    Notation('turtle', 'ttl', 'text/turtle', 'http://www.w3.org/ns/formats/Turtle')])


def convert(string, from_, to_):
    if from_ == to_:
        return encoded(string)
    assert from_ in FORMATS and to_ in FORMATS
    g = Graph()
    g.parse(StringIO(encoded(string)), format=from_)
    out = StringIO()
    g.serialize(out, format=to_)
    out.seek(0)
    return out.read()
