<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Dataset"/>
    % if ctx.date:
    <dcterms:date>${ctx.date.isoformat()}</dcterms:date>
    % endif
    % for contrib in ctx.contributor_assocs:
    <dcterms:contributor rdf:resource="${request.resource_url(contrib.contributor)}"/>
    % endfor
</%block>
