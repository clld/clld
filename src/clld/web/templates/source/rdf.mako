<%inherit file="../resource_rdf.mako"/>
<%! from clld.lib import rdf %>
<%! from clld.lib.bibo import TYPE_MAP, ADD_FIELD_MAP, FIELD_MAP %>
<%block name="properties">
    <rdf:type rdf:resource="${str(h.rdf.NAMESPACES['bibo']) + (TYPE_MAP.get(ctx.type) or 'bibo:Document').split(':')[1]}"/>

    ##% for l in request.db.query(h.models.Language).join(h.models.LanguageSource).filter(h.models.LanguageSource.source_pk == ctx.pk):
    % for l in ctx.languages:
    <dcterms:language rdf:resource="${request.resource_url(l)}"/>
    % endfor
    % if getattr(ctx, 'url', None):
    <dcterms:hasFormat>${ctx.url|h.xmlchars}</dcterms:hasFormat>
    % endif
    <dcterms:bibliographicCitation>
        ${ctx.bibtex().text()|h.xmlchars}
    </dcterms:bibliographicCitation>
    % if ctx.type in ADD_FIELD_MAP:
    <${ADD_FIELD_MAP[ctx.type][0]} rdf:resource="${ADD_FIELD_MAP[ctx.type][1]}"/>
    % endif
    % for field, spec in FIELD_MAP.items():
        % if getattr(ctx, field, None):
            % if isinstance(spec, tuple):
    <${spec[0]} rdf:parseType="Resource">
        <rdf:type rdf:resource="${rdf.url_for_qname(spec[1][0])}"/>
        <${spec[1][1]}>${getattr(ctx, field)|h.xmlchars}</${spec[1][1]}>
    </${spec[0]}>
            % else:
    <${spec}>${getattr(ctx, field)|h.xmlchars}</${spec}>
            % endif
        % endif
    % endfor
</%block>
