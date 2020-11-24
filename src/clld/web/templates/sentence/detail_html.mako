<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sentences" %>

<%def name="sidebar()">
    % if ctx.value_assocs:
    <%util:well title="${_('Datapoints')}">
        <ul>
        % for va in ctx.value_assocs:
            % if va.value:
            <li>${h.link(request, va.value.valueset, label='%s: %s' % (va.value.valueset.parameter.name, va.value.domainelement.name if va.value.domainelement else va.value.name))}</li>
            % endif
        % endfor
        </ul>
    </%util:well>
    % endif
</%def>

<h2>${_('Sentence')} ${ctx.id}</h2>
<dl>
    <dt>${_('Language')}:</dt>
    <dd>${h.link(request, ctx.language)}</dd>
</dl>

${h.rendered_sentence(ctx)|n}

<dl>
% if ctx.comment:
<dt>${_('Comment')}:</dt>
<dd>${ctx.markup_comment or ctx.comment|n}</dd>
% endif
% if ctx.source:
<dt>${_('Type')}:</dt>
<dd>${ctx.type}</dd>
% endif
% if ctx.references or ctx.source:
<dt>${_('Source')}:</dt>
% if ctx.source:
<dd>${ctx.source}</dd>
% endif
% if ctx.references:
<dd>${h.linked_references(request, ctx)|n}</dd>
% endif
% endif
</dl>
