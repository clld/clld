<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    <dcterms:isPartOf rdf:resource="${request.resource_url(ctx.valueset)}"/>
    % if ctx.domainelement_pk:
    <dcterms:conformsTo rdf:resource="${ctx.domainelement.url(request)}"/>
    % endif
    % if ctx.frequency is not None:
        <dcterms:description rdf:datatype="http://www.w3.org/2001/XMLSchema#float">${ctx.frequency}</dcterms:description>
    % endif
    ##confidence = Column(
    ##    Unicode, doc='textual assessment of the reliability of the value assignment')
    % for ref in getattr(ctx, 'references', []):
        <dcterms:references rdf:resource="${request.resource_url(ref.source)}"/>
    % endfor
</%block>
