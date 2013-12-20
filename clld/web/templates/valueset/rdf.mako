<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    % if ctx.language_pk:
    <dcterms:references rdf:resource="${request.resource_url(ctx.language)}"/>
    % endif
    % if ctx.parameter_pk:
    <dcterms:references rdf:resource="${request.resource_url(ctx.parameter)}"/>
    % endif
    % if ctx.contribution_pk:
    <dcterms:isPartOf rdf:resource="${request.resource_url(ctx.contribution)}"/>
    % endif
    % for v in ctx.values:
    <dcterms:hasPart rdf:resource="${request.resource_url(v)}"/>
    % endfor
</%block>
