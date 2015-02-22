
Linked Data
===========

CLLD applications publish Linked Data as follows:

1. `VoID description <http://www.w3.org/TR/void/>`_ deployed at <base-url>/void.ttl (also via content negotiation)
2. RDF serializations for each resource available via content negotiation or by appending
   a suitable file extension.
3. dumps pointed to from the VoID description

CLLD core resources provide serializations to RDF+XML via mako templates.
This serialization is used as the basis for all other RDF notations.
The core templates can be overwritten by applications using standard mako overrides.
Custom resources can also contribute additional triples to the core serialization
by specifying a __rdf__ method.


Vocabularies
------------

Types
~~~~~

Resources modelled as clld.db.models.common.Language are assigned dcterm's
`LinguisticSystem <http://dublincore.org/documents/2012/06/14/dcmi-terms/?v=terms#LinguisticSystem>`_ class
or additionally a subclasses of GOLD's
`Genetic Taxon <http://linguistics-ontology.org/gold/2010/GeneticTaxon>`_
or additionally the type
`skos:Concept <http://www.w3.org/TR/2009/REC-skos-reference-20090818/#concepts>`_.

clld.db.models.common.Source are assigned types from the
`Bibliographical Ontology <http://bibliontology.com/>`_.



Design decisions
----------------

1. No `"303 See other" <http://www.w3.org/TR/2008/NOTE-cooluris-20081203/>`_-type of
redirection. While this approach may be suitable to
distinguish between real-world objects and web documents, it also blows up the space
of URLs which need to be maintained, and raises the requirements for an application
serving the linked data (i.e. a simple web server serving static files will no longer do,
at least without complicated configuration). Since we want to make sure, that the data of
the CLLD project can be made available as Linked Data for as long as possible, minimizing
the requirements on the hosting requirement was regarded more important than sticking to
the best practice of using "303 See other"-type redirects.
