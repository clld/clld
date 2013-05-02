<% format = request.params.get('format', 'md.txt') %>
<%def name="li(_format, title)">
    <% url = request.route_url('contribution_alt', id=ctx.id, ext='md.html', _query=dict(format=_format)) %>
    <li class="${'active' if format == _format else ''}">
        <a onclick='${h.JSModal.show(ctx.name, url)|n}; return false'
           href='#'>
            ${title}
        </a>
    </li>
</%def>
##
## TODO: must get list of available formats from registry!
##
<ul class="nav nav-tabs">
    ${li('md.txt', _('Text'))}
    ${li('md.bib', _('BibTex'))}
##    ${li('ris', 'RIS')}
</ul>
<% from clld.web.adapters import get_adapter %>
<% adapter = get_adapter(h.interfaces.IMetadata, ctx, request, ext=format) %>
<pre>
${adapter.render(ctx, request)}
</pre>
