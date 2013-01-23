<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>

<%! from clld.interfaces import IDataTable %>
<%! from clld.db.models.common import Value %>

<h2>${_('Parameter')} ${ctx.name}</h2>

% if request.map:
${request.map.render()}
% endif


<div>
    <% dt = request.registry.getUtility(IDataTable, 'values'); dt = dt(request, Value, parameter=ctx) %>
    ${dt.render()}
</div>
