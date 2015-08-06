<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    % if ctx.language_pk:
    <dcterms:language rdf:resource="${request.resource_url(ctx.language)}"/>
    % endif
    % if ctx.parameter_pk:
    <dcterms:isPartOf rdf:resource="${request.resource_url(ctx.parameter)}"/>
    % endif
    % if ctx.contribution_pk:
    <void:inDataset rdf:resource="${request.resource_url(ctx.contribution)}"/>
    % endif
    % if ctx.source:
        <dcterms:source>${ctx.source}</dcterms:source>
    % endif
    % for v in ctx.values:
    <dcterms:hasPart rdf:resource="${request.resource_url(v)}"/>
    % endfor
    % for ref in ctx.references:
        <dcterms:references rdf:resource="${request.resource_url(ref.source)}"/>
    % endfor
</%block>
