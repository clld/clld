<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    % if ctx.latitude is not None and ctx.longitude is not None:
    <geo:long rdf:datatype="${h.rdf.url_for_qname('xsd:float')}">${ctx.longitude}</geo:long>
    <geo:lat rdf:datatype="${h.rdf.url_for_qname('xsd:float')}">${ctx.latitude}</geo:lat>
    % endif
    <rdf:type rdf:resource="http://purl.org/dc/terms/LinguisticSystem"/>
    % for identifier in ctx.identifiers:
    % if identifier.type == 'name' and identifier.name != ctx.name:
    <skos:altLabel${' xml:lang="'+identifier.lang+'"' if identifier.lang and len(identifier.lang) <= 3 else ''|n}>${identifier}</skos:altLabel>
    % endif
    % endfor
    % for source in ctx.sources:
    <dcterms:description rdf:resource="${request.resource_url(source)}"/>
    % endfor
    % if ctx.iso_code:
    <lexvo:iso639P3PCode rdf:datatype="${h.rdf.url_for_qname('xsd:string')}">${ctx.iso_code}</lexvo:iso639P3PCode>
    <owl:sameAs rdf:resource="http://dbpedia.org/resource/ISO_639:${ctx.iso_code}"/>
    % endif
    % if request.dataset.id != 'glottolog' and ctx.glottocode:
    <owl:sameAs rdf:resource="http://glottolog.org/resource/languoid/id/${ctx.glottocode}"/>
    % endif
    % for vs in ctx.valuesets:
    <dcterms:isReferencedBy rdf:resource="${request.resource_url(vs)}"/>
    % endfor
</%block>
