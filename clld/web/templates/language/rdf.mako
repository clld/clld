<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    % if ctx.latitude is not None and ctx.longitude is not None:
    <geo:long>${ctx.longitude}</geo:long>
    <geo:lat>${ctx.latitude}</geo:lat>
    % endif
    <rdf:type rdf:resource="http://purl.org/dc/terms/LinguisticSystem"/>
    ## TODO: skos:altLabel for names, identifiers?
    % for identifier in ctx.identifiers:
    % if identifier.type == 'name' and identifier.name != ctx.name:
    <skos:altLabel${' xml:lang="'+identifier.lang+'"' if identifier.lang and len(identifier.lang) <= 3 else ''|n}>${identifier}</skos:altLabel>
    % endif
    % endfor
    ##% for source in request.db.query(h.models.Source).join(h.models.LanguageSource).filter(h.models.LanguageSource.language_pk == ctx.pk):
    % for source in ctx.sources:
    <dcterms:isReferencedBy rdf:resource="${request.resource_url(source)}"/>
    % endfor
    % if ctx.iso_code:
    <lexvo:iso639P3PCode rdf:datatype="xsd:string">${ctx.iso_code}</lexvo:iso639P3PCode>
    <owl:sameAs rdf:resource="http://dbpedia.org/resource/ISO_639:${ctx.iso_code}"/>
    % endif
    % if ctx.glottocode:
    <owl:sameAs rdf:resource="http://glottolog.org/resource/languoid/id/${ctx.glottocode}"/>
    % endif
    % for vs in ctx.valuesets:
    <dcterms:isReferencedBy rdf:resource="${request.resource_url(vs)}"/>
    % endfor
</%block>
