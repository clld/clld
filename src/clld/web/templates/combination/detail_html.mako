<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%! from clld.web.util.multiselect import CombinationMultiSelect %>
<%block name="title">${_('Combination')} ${ctx.name}</%block>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/select2.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/select2.js')}"></script>
</%block>

<h3>${_('Combination')} ${' / '.join(h.link(request, p) for p in ctx.parameters)|n}</h3>

% if len(ctx.parameters) < 4:
<div>
    <form action="${request.route_url('select_combination')}">
        <fieldset>
            <p>
                You may combine these ${_('Parameters').lower()} with another one.
                Start typing the ${_('Parameter').lower()} name or number in the field below.
            </p>
            <% select = CombinationMultiSelect(request, combination=ctx) %>
            ${select.render()}
            <button class="btn" type="submit">Submit</button>
        </fieldset>
    </form>
</div>
% endif

% if multivalued:
<div class="alert alert-info">
    <strong>Note:</strong> Languages may have multiple values marked with
    overlapping markers. These languages are additionally marked with a small red
    triangle. Clicking on this marker will show all value markers associated with the
    language.
</div>
% endif

% if request.map:
${request.map.render()}
% endif

% if ctx.domain:
<div id="list-container">
    ${util.combination_valuetable(ctx, iconselect=iconselect or False)}
</div>
% endif
