<%namespace name="util" file="../util.mako"/>

<% format = request.params.get('format', 'txt') %>

<%def name="li(_format, title)">
    <% url = request.route_url('source_alt', id=ctx.id, ext='snippet.html', _query=dict(format=_format)) %>
    <li class="${'active' if format == _format else ''}">
        <a onclick='$("#md-${ctx.id}").load(${h.dumps(url)}); return false'
           href='#'>
            ${title}
        </a>
    </li>
</%def>

<div id="md-${ctx.id}" class="tabbable tabs-left">
    <ul class="nav nav-tabs">
        ${li('txt', 'Text')}
        ${li('bib', 'BibTex')}
    ##    ${li('ris', 'RIS')}
    </ul>
    ##<% from clld.web.adapters import get_adapter %>
    ##<% adapter = get_adapter(h.interfaces.IRepresentation, ctx, request, ext=format) %>
    ##<pre>
    ##${adapter.render(ctx, request)}
    ##</pre>
</div>
