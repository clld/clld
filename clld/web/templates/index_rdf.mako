<rdf:RDF ${h.rdf_namespace_attrs()|n}>
    <% rsc_name = request.matched_route.name.split('_')[0][:-1] %>
    <% member_urls = {r[0]: request.route_url(rsc_name, id=r[0]) for r in ctx} %>
    <skos:Collection rdf:about="${request.route_url(rsc_name + 's')}">
        <void:inDataset rdf:resource="${request.route_url('dataset')}"/>
        <rdfs:label xml:lang="en">${_(rsc_name.capitalize())}s</rdfs:label>
        <skos:prefLabel xml:lang="en">${_(rsc_name.capitalize())}s</skos:prefLabel>
        <dcterms:title xml:lang="en">${_(rsc_name.capitalize())}s</dcterms:title>
        <skos:hiddenLabel xml:lang="x-clld">${rsc_name}</skos:hiddenLabel>
        <skos:scopeNote xml:lang="x-clld">index</skos:scopeNote>
        % for row in ctx:
        <skos:member rdf:resource="${member_urls[row[0]]}"/>
        % endfor
    </skos:Collection>
% for row in [r for r in ctx if r[1]]:
    <rdf:Description rdf:about="${member_urls[row[0]]}">
        <rdfs:label xml:lang="en">${row[1] or ''}</rdfs:label>
        <dcterms:identifier>${row[0]}</dcterms:identifier>
    </rdf:Description>
% endfor
</rdf:RDF>
