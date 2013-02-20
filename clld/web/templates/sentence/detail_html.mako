<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sentences" %>


<h2>${_('Sentence')} ${ctx.id}</h2>
<dl>
    <dt>Language:</dt>
    <dd>${h.link(request, ctx.language)}</dd>
    <dt>Text:</dt>
    <dd>${ctx.name}</dd>
% if ctx.analyzed:
<dt>Analyzed text:</dt>
<dd>${ctx.analyzed}</dd>
% endif
% if ctx.gloss:
<dt>Gloss:</dt>
<dd>${ctx.gloss}</dd>
% endif
% if ctx.description:
<dt>Translation:</dt>
<dd>${ctx.description}</dd>
% endif
% if ctx.comment:
<dt>Comment:</dt>
<dd>${ctx.comment}</dd>
% endif
% if ctx.source:
<dt>Source:</dt>
<dd>${ctx.source}</dd>
% endif
% if ctx.references:
<dt>References</dt>
<dd>
    <ul class="unstyled">
        % for ref in ctx.references:
        <li>
            ${h.link(request, ref.source)} ${'(' + ref.description + ')' if ref.description else ''}
        </li>
        % endfor
    </ul>
</dd>
% endif
</dl>
