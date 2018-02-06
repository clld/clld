<rdf:RDF ${h.rdf_namespace_attrs()|n}>
    <rdf:Description rdf:about="${request.resource_url(ctx)}">
        <void:inDataset rdf:resource="${request.route_url('dataset')}"/>
        <rdfs:label xml:lang="en">${ctx}</rdfs:label>
        <skos:prefLabel xml:lang="en">${ctx}</skos:prefLabel>
        % if h.get_resource_type(ctx):
            <skos:scopeNote xml:lang="x-clld">${h.get_resource_type(ctx)}</skos:scopeNote>
        % endif
        <skos:altLabel xml:lang="x-clld">${getattr(ctx, 'id', None)}</skos:altLabel>
        <dcterms:title xml:lang="en">${ctx}</dcterms:title>
        % if getattr(ctx, 'description', None):
        <dcterms:description xml:lang="en">${ctx.description}</dcterms:description>
        % endif
        <%block name="properties"></%block>
        % if callable(getattr(ctx, '__rdf__', None)):
        ${h.rdf.properties_as_xml_snippet(request.resource_url(ctx), ctx.__rdf__(request))|n}
        % endif
    </rdf:Description>
    <%block name="resources"></%block>
</rdf:RDF>
