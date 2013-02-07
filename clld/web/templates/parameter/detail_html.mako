<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>

<h2>${_('Parameter')} ${ctx.name}</h2>

% if request.map:
${request.map.render()}
% endif

<div>
    <% dt = request.registry.getUtility(h.interfaces.IDataTable, 'values'); dt = dt(request, h.models.Value, parameter=ctx) %>
    ${dt.render()}
</div>
