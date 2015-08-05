<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    % if ctx.unit_pk:
        <dcterms:relation rdf:resource="${request.resource_url(ctx.unit)}"/>
    % endif
    % if ctx.unitparameter_pk:
        <dcterms:isPartOf rdf:resource="${request.resource_url(ctx.unitparameter)}"/>
    % endif
    % if ctx.contribution_pk:
        <void:inDataset rdf:resource="${request.resource_url(ctx.contribution)}"/>
    % endif
    % if ctx.unitdomainelement_pk:
        <dcterms:conformsTo rdf:resource="${ctx.unitdomainelement.url(request)}"/>
    % endif
</%block>
