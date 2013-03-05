<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>${_('Value Set')} ${h.link(request, ctx.language)}/${h.link(request, ctx.parameter)}</h2>

<dl>
    <dt>Language:</dt>
    <dd>${h.link(request, ctx.language)}</dd>
    <dt>Parameter:</dt>
    <dd>${h.link(request, ctx.parameter)}</dd>
    % if ctx.references:
    <dt>References</dt>
    <dd>${h.linked_references(ctx)|n}</dd>
    % endif
    % for k, v in ctx.datadict().items():
    <dt>${k}</dt>
    <dd>${v}</dd>
    % endfor
</dl>

<h3>${_('Values')}</h3>
<ul class="unstyled">
% for value in ctx.values:
<li>
${h.link(request, value)}
##
## TODO: frequency, confidence!
##
% if value.sentence_assocs:
<h4>${_('Sentences')}</h4>
<ol>
    % for a in value.sentence_assocs:
    <li>
        % if a.description:
        <p>${a.description}</p>
        % endif
        ${h.rendered_sentence(a.sentence)}
        % if a.sentence.references:
        <p>See ${h.linked_references(a.sentence)|n}</p>
        % endif
    </li>
    % endfor
</ol>
% endif
</li>
% endfor
</ul>
