<rdf:RDF  ${h.rdf_namespace_attrs()|n}>
    <%! from clld.lib.rdf import FORMATS %>
    <%! from clld import RESOURCES, __version__ %>
    <% rscs = [rsc for rsc in RESOURCES if rsc.name != 'testresource' and rsc.with_index] %>
    <% sitemaps = request.registry.settings.get('clld.sitemaps', []) %>
    <% TxtCitation = h.get_adapter(h.interfaces.IRepresentation, ctx, request, ext='md.txt') %>
    <void:Dataset rdf:about="${request.route_url('dataset')}">
        <rdfs:label xml:lang="en">${request.dataset.name}</rdfs:label>
        <skos:prefLabel xml:lang="en">${request.dataset.name}</skos:prefLabel>
        <dcterms:title xml:lang="en">${request.dataset.name}</dcterms:title>
        % if request.dataset.description:
        <dcterms:description xml:lang="en">${request.dataset.description}</dcterms:description>
        % endif
        <skos:scopeNote xml:lang="x-clld">dataset</skos:scopeNote>
        <skos:altLabel xml:lang="x-clld">${ctx.id}</skos:altLabel>
        <foaf:homepage>${request.route_url('dataset')}</foaf:homepage>
        <dcterms:license rdf:resource="${request.dataset.license}"/>
        <dcterms:rightsHolder rdf:resource="${request.dataset.publisher_url}"/>
        <dcterms:publisher rdf:resource="${request.dataset.publisher_url}"/>
        % for format in FORMATS.values():
        <void:feature rdf:resource="${format.uri}"/>
        % endfor
        % for rsc in [_r for _r in rscs if _r.name in sitemaps]:
        <void:subset rdf:resource="${request.route_url(rsc.name + 's')}"/>
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
    % if dls or (rsc.name in sitemaps):
    <void:Dataset rdf:about="${request.route_url(rsc.name + 's')}">
        <skos:prefLabel xml:lang="en">${_(rsc.name.capitalize())}s</skos:prefLabel>
        <skos:hiddenLabel xml:lang="x-clld">${rsc.name}</skos:hiddenLabel>
        <skos:example>${request.route_url(rsc.name, id='---').replace('---', '{id}')}</skos:example>
        % if dls:
            % for dl in dls:
            <void:dataDump rdf:resource="${dl.url(request)}"/>
            % endfor
        % else:  ## rsc.name in sitemaps
        <void:rootResource rdf:resource="${request.route_url(rsc.name + 's')}"/>
        % endif
    </void:Dataset>
    % endif
% endfor
    <foaf:Organization rdf:about="${request.dataset.publisher_url}">
        <skos:prefLabel xml:lang="en">${request.dataset.publisher_name}</skos:prefLabel>
        <foaf:homepage>${request.dataset.publisher_url}</foaf:homepage>
        % if request.dataset.contact:
            <foaf:mbox>${request.dataset.contact}</foaf:mbox>
        % endif
    </foaf:Organization>
    <dctype:Software rdf:about="https://github.com/clld/clld">
        <dcterms:identifier rdf:resource="https://github.com/clld/clld/releases/tag/${__version__}"/>
    </dctype:Software>
</rdf:RDF>
