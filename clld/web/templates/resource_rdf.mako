<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:void="http://rdfs.org/ns/void#"
         xmlns:foaf="http://xmlns.com/foaf/0.1/"
         xmlns:frbr="http://purl.org/vocab/frbr/core#"
         xmlns:dcterms="http://purl.org/dc/terms/"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
         xmlns:isbd="http://iflastandards.info/ns/isbd/elements/"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:gold="http://purl.org/linguistics/gold/"
         xmlns:lexvo="http://lexvo.org/ontology"
         xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#"
         xmlns:bibo="http://purl.org/ontology/bibo/"
         xmlns:owl="http://www.w3.org/2002/07/owl#">
    <rdf:Description rdf:about="${request.resource_url(ctx)}">
        <void:inDataset rdf:resource="${request.route_url('dataset')}"/>
        <rdfs:label xml:lang="en">${ctx}</rdfs:label>
        <skos:prefLabel xml:lang="en">${ctx}</skos:prefLabel>
        <dcterms:title xml:lang="en">${ctx}</dcterms:title>
        % if hasattr(ctx, 'description'):
        <dcterms:description xml:lang="en">${ctx.description}</dcterms:description>
        % endif
        <%block name="properties"></%block>
    </rdf:Description>
</rdf:RDF>
