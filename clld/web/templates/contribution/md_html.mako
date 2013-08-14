<%namespace name="util" file="../util.mako"/>
<% format = request.params.get('format', 'md.txt') %>
<ul class="nav nav-tabs">
    ${util.md_tab_li('md.txt', 'contribution', _('Text'))|n}
    ${util.md_tab_li('md.bib', 'contribution', _('BibTex'))}
##    ${li('ris', 'RIS')}
</ul>
<% from clld.web.adapters import get_adapter %>
<% adapter = get_adapter(h.interfaces.IMetadata, ctx, request, ext=format) %>
% if format == 'md.bib':
<pre>
${adapter.render(ctx, request)}
</pre>
% else:
<blockquote>
${h.text2html(adapter.render(ctx, request))|n}
</blockquote>
% endif
