<rdf:RDF  ${h.rdf_namespace_attrs()|n}>
    <%! from clld.lib.rdf import FORMATS %>
    <%! from clld import RESOURCES %>
    <% rscs = [rsc for rsc in RESOURCES if rsc.name != 'testresource'] %>
    <% TxtCitation = h.get_adapter(h.interfaces.IRepresentation, ctx, request, ext='md.txt') %>
    <void:Dataset rdf:about="${request.route_url('dataset')}">
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
        % for rsc in rscs:
            % if rsc.name in request.registry.settings.get('sitemaps', []) and rsc.with_index:
        <void:subset rdf:resource="${request.route_url(rsc.name + 's')}"/>
            % endif
        % endfor
        ##<dcterms:creator>Glottolog 2.0</dcterms:creator>
        % for ed in request.dataset.editors:
        <dcterms:contributor rdf:parseType="Resource">
            <rdf:type rdf:resource="${h.rdf.url_for_qname('foaf:Person')}"/>
            <foaf:name>${ed.contributor}</foaf:name>
        </dcterms:contributor>
        % endfor
        <dcterms:bibliographicCitation>
${TxtCitation.render(request.dataset, request)}
        </dcterms:bibliographicCitation>
        <dcterms:subject rdf:resource="http://dbpedia.org/resource/Linguistics"/>
    </void:Dataset>
% for rsc in rscs:
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
