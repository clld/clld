<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    <dcterms:language rdf:resource="${request.resource_url(ctx.language)}"/>
</%block>
