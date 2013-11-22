<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>${_('Value')} ${ctx.domainelement.name if ctx.domainelement else ctx.name}</h2>

<dl>
    <dt>Language:</dt>
    <dd>${h.link(request, ctx.valueset.language)}</dd>
    <dt>Parameter:</dt>
    <dd>${h.link(request, ctx.valueset.parameter)}</dd>
    % if ctx.valueset.references:
    <dt>References</dt>
    <dd>${h.linked_references(request, ctx.valueset)|n}</dd>
    % endif
    % for k, v in ctx.datadict().items():
    <dt>${k}</dt>
    <dd>${v}</dd>
    % endfor
</dl>

% if ctx.sentence_assocs:
<h3>${_('Sentences')}</h3>
<ol>
    % for a in ctx.sentence_assocs:
    <li>
        % if a.description:
        <p>${a.description}</p>
        % endif
        ${h.rendered_sentence(a.sentence)}
        % if a.sentence.references:
        <p>See ${h.linked_references(request, a.sentence)|n}</p>
        % endif
    </li>
    % endfor
</ol>
% endif
