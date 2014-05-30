<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    % if ctx.date:
    <dcterms:date>${ctx.date.isoformat()}</dcterms:date>
    % endif
    % for contrib in ctx.contributor_assocs:
    <dcterms:contributor rdf:resource="${request.resource_url(contrib.contributor)}">
    </dcterms:contributor>
    % endfor
</%block>
