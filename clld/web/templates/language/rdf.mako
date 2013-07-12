<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    % if ctx.latitude is not None and ctx.longitude is not None:
    <geo:long>${ctx.longitude}</geo:long>
    <geo:lat>${ctx.latitude}</geo:lat>
    % endif
    <rdf:type rdf:resource="http://purl.org/dc/terms/LinguisticSystem"/>
</%block>
