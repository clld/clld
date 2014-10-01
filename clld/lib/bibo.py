"""
Functionality for the creation of bibliographical data using the Bibliographic Ontology.

.. seealso:: http://bibliontology.com/
"""
#: Map BibTeX entry types to the corresponding bibo types.
TYPE_MAP = {
    "book": "bibo:Book",
    "booklet": "bibo:Book",
    "misc": "bibo:Document",
    "article": "bibo:Article",
    "inbook": "bibo:Chapter",
    "manual": "bibo:Manual",
    "inproceedings": "bibo:Article",
    "conference": "bibo:Article",
    "unpublished": "bibo:Document",
    "masterthesis": "bibo:Thesis",
    "phdthesis": "bibo:Thesis",
    "proceedings": "bibo:Proceedings",
    "techreport": "bibo:Report",
    "incollection": "bibo:BookSection",
    "heading": "bibo:Collection",
    "subject": "skos:Concept",
    "person": "foaf:Person",
}


ADD_FIELD_MAP = {
    "unpublished": ("bibo:status", "http://purl.org/ontology/bibo/status/unpublished"),
    "masterthesis": ("bibo:degree", "http://purl.org/ontology/bibo/degrees/ma"),
    "phdthesis": ("bibo:degree", "http://purl.org/ontology/bibo/degrees/phd"),
}


FIELD_MAP = {
    "title": "dcterms:title",
    "author": ("dcterms:creator", ("foaf:Agent", "foaf:name")),
    "booktitle": "dcterms:title",
    "publisher": ("dcterms:publisher", ("foaf:Organization", "foaf:name")),
    "year": "dcterms:date",
    "month": "dcterms:date",
    "isbn": "bibo:isbn",
    "editor": ("bibo:editor", ("foaf:Person", "foaf:name")),
    "institution": ("dcterms:contributor", ("foaf:Organization", "foaf:name")),
    "volume": "bibo:volume",
    "type": "dcterms:type",
    "series": ("dcterms:isPartOf", ("bibo:Series", "dcterms:title")),
    "school": ("rdfs:seeAlso", ("foaf:Organization", "foaf:name")),
    "pages": "bibo:pages",
    "organization": ("bibo:organizer", ("foaf:Organization", "foaf:name")),
    "number": "bibo:number",
    "note": "skos:note",
    "journal": ("dcterms:isPartOf", ("bibo:Journal", "dcterms:title")),
    "edition": "bibo:edition",
    "chapter": "bibo:chapter",
    "address": "vcard:locality",
    "eprint": "rdfs:seeAlso",
    "crossref": "dcterms:isPartOf",
    "name": "foaf:name",
    "updated": "dcterms:modified",
    "bibliography": "foaf:page",
    "honor": "foaf:page",
    "biography": "foaf:page",
    "comment": "skos:note",
    "rev": "dcterms:modified",
    "date": "dcterms:date",
    "howpublished": "dcterms:publisher",
    "keywords": "dcterms:subject",
    "abstract": "bibo:abstract",
    "description": "dcterms:description",
}
