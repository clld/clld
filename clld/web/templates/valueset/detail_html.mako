<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>${_('Value Set')} ${h.link(request, ctx.language)}/${h.link(request, ctx.parameter)}</h2>

% if ctx.description:
<p>${h.text2html(ctx.description)}</p>
% endif

<h3>${_('Values')} ${h.map_marker_img(request, ctx, height='25', width='25')|n}</h3>

<div class="accordion" id="values-accordion">
    % for value in ctx.values:
    <%util:accordion_group eid="acc-${value.id}" parent="values-accordion" open="${False}">
        <%def name="title()">
            ${h.map_marker_img(request, value)}
            <b>${value.domainelement.name if value.domainelement else (value.name or value.id)}</b>
            ${h.format_frequency_and_confidence(value)}
        </%def>
        % if value.sentence_assocs:
        <h4>${_('Sentences')}</h4>
        ${util.sentences(value)}
        % else:
        no sentences
        % endif
    </%util:accordion_group>
    % endfor
</div>

<%def name="sidebar()">
<div class="well well-small">
<dl>
    <dt>${_('Contribution')}:</dt>
    <dd>
        ${h.link(request, ctx.contribution)}
        by
        ${h.linked_contributors(request, ctx.contribution)}
        ${h.button('cite', onclick=h.JSModal.show(ctx.contribution.name, request.resource_url(ctx.contribution, ext='md.html')))}
    </dd>
    <dt>${_('Language')}:</dt>
    <dd>${h.link(request, ctx.language)}</dd>
    <dt>${_('Parameter')}:</dt>
    <dd>${h.link(request, ctx.parameter)}</dd>
    % if ctx.references:
    <dt>${_('References')}:</dt>
    <dd>${h.linked_references(request, ctx)|n}</dd>
    % endif
    ${util.data(ctx, with_dl=False)}
</dl>
</div>
</%def>
