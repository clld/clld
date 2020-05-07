<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} ${ctx.name}</%block>

{% if cookiecutter.cldf_module.lower() == 'structuredataset' %}
<div class="span4" style="float: right; margin-top: 1em;">
    <%util:well title="Values">
        <table class="table table-condensed">
            % for de in ctx.domain:
            <tr>
                <td>${h.map_marker_img(req, de)}</td>
                <td>${de.name}</td>
                <td>${de.description}</td>
                <td class="right">${len(de.values)}</td>
            </tr>
            % endfor
        </table>
    </%util:well>
</div>
{% endif %}

<h2>${_('Parameter')} ${ctx.name}</h2>

% if ctx.description:
<p>${ctx.description}</p>
% endif

<div style="clear: both"/>
% if map_ or request.map:
${(map_ or request.map).render()}
% endif

${request.get_datatable('values', h.models.Value, parameter=ctx).render()}
