<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Combination')} ${ctx.name}</%block>

<h2>${_('Combination')} ${ctx.name}</h2>

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
