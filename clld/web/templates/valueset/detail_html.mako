<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>${_('Value Set')} ${h.link(request, ctx.language)}/${h.link(request, ctx.parameter)}</h2>

% if ctx.description:
${h.text2html(h.Markup(ctx.markup_description) if ctx.markup_description else ctx.description, mode='p')}
% endif

<h3>${_('Values')} ${h.map_marker_img(request, ctx, height='25', width='25')|n}</h3>
% for i, value in enumerate(ctx.values):
<div style="clear: right;">
    <ul class="nav nav-pills pull-right">
        <li><a data-toggle="collapse" data-target="#s${i}">Show/hide details</a></li>
    </ul>
    <h4>
        ${h.map_marker_img(request, value)}
        ${value.__unicode__()}
        ${h.format_frequency(request, value)}
    </h4>
    <div id="s${i}" class="collapse in">
        ${util.sentences(value)}
        % if value.confidence:
        <dl>
            <dt>${_('Confidence')}:</dt>
            <dd>${value.confidence}</dd>
        </dl>
        % endif
    </div>
</div>
% endfor
<%def name="sidebar()">
<div class="well well-small">
<dl>
    <dt class="contribution">${_('Contribution')}:</dt>
    <dd class="contribution">
        ${h.link(request, ctx.contribution)}
        by
        ${h.linked_contributors(request, ctx.contribution)}
        ${h.button('cite', onclick=h.JSModal.show(ctx.contribution.name, request.resource_url(ctx.contribution, ext='md.html')))}
    </dd>
    <dt class="language">${_('Language')}:</dt>
    <dd class="language">${h.link(request, ctx.language)}</dd>
    <dt class="parameter">${_('Parameter')}:</dt>
    <dd class="parameter">${h.link(request, ctx.parameter)}</dd>
    % if ctx.references or ctx.source:
    <dt class="source">${_('Source')}:</dt>
        % if ctx.source:
        <dd>${ctx.source}</dd>
        % endif
        % if ctx.references:
        <dd class="source">${h.linked_references(request, ctx)|n}</dd>
        % endif
    % endif
    ${util.data(ctx, with_dl=False)}
</dl>
</div>
</%def>
