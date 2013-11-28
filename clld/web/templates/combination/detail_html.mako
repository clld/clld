<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%! from clld.web.util.multiselect import CombinationMultiSelect %>
<%block name="title">${_('Combination')} ${ctx.name}</%block>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/select2.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/select2.js')}"></script>
</%block>

<h2>${_('Combination')} ${ctx.name}</h2>

% if len(ctx.parameters) < 4:
<div>
    <form action="${request.route_url('select_combination')}">
        <fieldset>
            <p>
                You may combine these ${_('Parameters').lower()} with another one.
                Start typing the feature name or number in the field below.
            </p>
            <% select = CombinationMultiSelect(request, combination=ctx) %>
            ${select.render()}
            <button class="btn" type="submit">Submit</button>
        </fieldset>
    </form>
</div>
% endif

<div class="alert alert-info">
    <strong>Note:</strong> Languages may have multiple values marked with
    overlapping markers. These languages are additionally marked with a small red
    triangle. Clicking on this marker will show all value markers associated with the
    language.
</div>

% if request.map:
${request.map.render()}
% endif

% if ctx.domain:
<div id="list-container">
    <table class="table table-nonfluid">
        <thead>
            <th> </th>
            <th> </th>
            <th>${' / '.join(h.link(request, p) for p in ctx.parameters)|n}</th>
            <th>Number of languages</th>
        </thead>
        <tbody>
            % for i, de in enumerate(ctx.domain):
            <tr>
                <td>
                    % if de.languages:
                    <button title="click to toggle display of languages for value ${de.name}"
                            type="button" class="btn btn-mini expand-collapse" data-toggle="collapse" data-target="#de-${i}">
                        <i class="icon icon-plus"> </i>
                    </button>
                    % endif
                </td>
                <td>
                    % if de.languages:
                    <img height="20" width="20" src="${de.icon.url(request)}"/>
                    % endif
                </td>
                <td>
                    ${de.name}
                    <div id="de-${i}" class="collapse">
                        <table class="table table-condensed table-nonfluid">
                            <tbody>
                                % for language in de.languages:
                                <tr>
                                    <td>${h.link_to_map(language)}</td>
                                    <td>${h.link(request, language)}</td>
                                </tr>
                                % endfor
                            </tbody>
                        </table>
                    </div>
                </td>
                <td style="text-align: right;">${str(len(de.languages))}</td>
            </tr>
            % endfor
        </tbody>
    </table>
</div>
<script>
$(document).ready(function() {
    $('.expand-collapse').click(function(){ //you can give id or class name here for $('button')
        $(this).children('i').toggleClass('icon-minus icon-plus');
    });
});
</script>
% endif
