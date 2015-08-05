<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    <dcterms:language rdf:resource="${request.resource_url(ctx.language)}"/>
    <dcterms:description xml:lang="x-clld-IGT-analyzed">${ctx.analyzed or ''}</dcterms:description>
    <dcterms:description xml:lang="x-clld-IGT-gloss">${ctx.gloss or ''}</dcterms:description>
    <dcterms:description xml:lang="x-clld-IGT-original-script">${ctx.original_script or ''}</dcterms:description>
    <dcterms:type>${ctx.type or ''}</dcterms:type>
    <dcterms:source>${ctx.source or ''}</dcterms:source>
    <skos:note>${ctx.comment or ''}</skos:note>
    % for ref in ctx.references:
        <dcterms:references rdf:resource="${request.resource_url(ref.source)}"/>
    % endfor
</%block>
