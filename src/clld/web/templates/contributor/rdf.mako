<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    <rdf:type rdf:resource="${h.rdf.url_for_qname('foaf:Person')}"/>
    % if ctx.email:
    <foaf:mbox rdf:resource="mailto:${ctx.email.split(',')[0]}"/>
    % endif
    % if ctx.url:
    <foaf:homepage rdf:resource="${ctx.url.split(',')[0]}"/>
    % endif
    % if ctx.address:
    <dcterms:spatial>${ctx.address}</dcterms:spatial>
    % endif
</%block>
