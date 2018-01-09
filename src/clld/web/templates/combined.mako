<%inherit file="${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "parameters" %>

<h3>Parameter combination</h3>

<div class="row-fluid">
    <div class="span6">
        <form>
            <fieldset>
                <legend>Select parameters</legend>
                ${select.render()}
                <br />
                <button class="btn" type="submit">Submit</button>
            </fieldset>
        </form>
    </div>
% if map:
    <div class="well well-small span6">
    <table class="table table-nonfluid">
        <thead>
            <tr><th>Marker</th><th>Parameter value</th></tr>
        </thead>
        <tbody>
    % for layer in map.layers:
        % if getattr(layer, 'domain', None):
            % for de in layer.domain:
            <tr>
                <td><img src="${de['icon']}" width="${layer.size}" height="${layer.size}"/></td>
                <td><a href="${layer.link}">${layer.name} - ${de['name']}</a></td>
            </tr>
            % endfor
        % else:
        <tr>
            <td>${layer.marker}</td>
            <td><a href="${layer.link}">${layer.name}</a></td>
        </tr>
        % endif
    % endfor
        </tbody>
    </table>
    </div>
% endif
</div>

% if map:
${map.render()}
% endif

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/select2.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/select2.js')}"></script>
    <style>
#legend-iconsize {display: none;}
    </style>
</%block>
