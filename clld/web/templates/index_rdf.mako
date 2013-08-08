<rdf:RDF ${h.rdf_namespace_attrs()|n}>
    <% rsc_name = request.matched_route.name.split('_')[0][:-1] %>
    <skos:Collection rdf:about="${request.route_url(rsc_name + 's')}">
        <void:inDataset rdf:resource="${request.route_url('dataset')}"/>
        <rdfs:label xml:lang="en">${_(ctx)}</rdfs:label>
        <skos:prefLabel xml:lang="en">${_(ctx)}</skos:prefLabel>
        <dcterms:title xml:lang="en">${_(ctx)}</dcterms:title>
        % for row in request.db.query(ctx.model.id):
        <skos:member rdf:resource="${request.route_url(rsc_name, id=row[0])}"/>
        % endfor
    </skos:Collection>
</rdf:RDF>
