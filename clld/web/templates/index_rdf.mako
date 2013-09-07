<rdf:RDF ${h.rdf_namespace_attrs()|n}>
    <% rsc_name = request.matched_route.name.split('_')[0][:-1] %>
    <skos:Collection rdf:about="${request.route_url(rsc_name + 's')}">
        <void:inDataset rdf:resource="${request.route_url('dataset')}"/>
        <rdfs:label xml:lang="en">${_(rsc_name)}s</rdfs:label>
        <skos:prefLabel xml:lang="en">${_(rsc_name)}s</skos:prefLabel>
        <dcterms:title xml:lang="en">${_(rsc_name)}s</dcterms:title>
        % for row in ctx:
        <skos:member rdf:resource="${request.route_url(rsc_name, id=row)}"/>
        % endfor
    </skos:Collection>
</rdf:RDF>
