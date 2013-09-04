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
    <%! from clld.lib.rdf import FORMATS %>
    <%! from clld import RESOURCES %>
    <% TxtCitation = h.get_adapter(h.interfaces.IRepresentation, ctx, request, ext='md.txt') %>
    <void:Dataset rdf:about="${request.route_url('dataset')}">
        ##
        ## TODO: license, publisher, subject, ...
        ##
        <rdfs:label xml:lang="en">${request.dataset.name}</rdfs:label>
        <skos:prefLabel xml:lang="en">${request.dataset.name}</skos:prefLabel>
        <dcterms:title xml:lang="en">${request.dataset.name}</dcterms:title>
        % if request.dataset.description:
        <dcterms:description xml:lang="en">${request.dataset.description}</dcterms:description>
        % endif
        <foaf:homepage>${request.route_url('dataset')}</foaf:homepage>
        <dcterms:license rdf:resource="${request.dataset.license}"/>
        <dcterms:rightsHolder rdf:resource="${request.dataset.publisher_url}"/>
        <dcterms:publisher rdf:resource="${request.dataset.publisher_url}"/>
        % for format in FORMATS.values():
        <void:feature rdf:resource="${format.uri}"/>
        % endfor
        % for rsc in RESOURCES:
            % if rsc.name in request.registry.settings.get('sitemaps', []) and rsc.with_index:
        <void:subset rdf:resource="${request.route_url(rsc.name + 's')}"/>
            % endif
        % endfor
        ##<dcterms:creator>Glottolog 2.0</dcterms:creator>
        % for ed in request.dataset.editors:
        <dcterms:contributor rdf:parseType="Resource">
            <rdf:type rdf:resource="foaf:Person"/>
            <foaf:name>${ed.contributor}</foaf:name>
        </dcterms:contributor>
        % endfor
        <dcterms:bibliographicCitation>
${TxtCitation.render(request.dataset, request)}
        </dcterms:bibliographicCitation>
        <dcterms:subject rdf:resource="http://dbpedia.org/resource/Linguistics"/>
    </void:Dataset>
% for rsc in RESOURCES:
    <% dls = list(h.get_rdf_dumps(request, rsc.model)) %>
    % if not dls:
        % if rsc.name in request.registry.settings.get('sitemaps', []) and rsc.with_index:
        <void:Dataset rdf:about="${request.route_url(rsc.name + 's')}">
            <void:rootResource rdf:resource="${request.route_url(rsc.name + 's')}"/>
        </void:Dataset>
        % endif
    % else:
        % if rsc.with_index:
        <void:Dataset rdf:about="${request.route_url(rsc.name + 's')}">
            % for dl in dls:
            <void:dataDump rdf:resource="${dl.url(request)}"/>
            % endfor
        </void:Dataset>
        % endif
    % endif
% endfor
    <foaf:Organization rdf:about="${request.dataset.publisher_url}">
        <skos:prefLabel xml:lang="en">${request.dataset.publisher_name}</skos:prefLabel>
        <foaf:homepage>${request.dataset.publisher_url}</foaf:homepage>
        <foaf:mbox>${request.dataset.id}@eva.mpg.de</foaf:mbox>
    </foaf:Organization>
</rdf:RDF>
