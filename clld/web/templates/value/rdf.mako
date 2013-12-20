<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    <dcterms:isPartOf rdf:resource="${request.resource_url(ctx.valueset)}"/>
    % if ctx.domainelement_pk:
    <dcterms:references rdf:resource="${request.resource_url(ctx.valueset.parameter, _anchor='DE-' + ctx.domainelement.id)}"/>
    % endif
</%block>
