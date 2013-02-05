<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>

<%! from clld.interfaces import IDataTable %>
<%! from clld.db.models.common import Value %>

<h2>${_('Contribution')} ${ctx.name}</h2>

${util.data()}

<% dt = request.registry.queryUtility(IDataTable, 'values'); dt = dt(request, Value, contribution=ctx) %>
% if dt:
<div>
    ${dt.render()}
</div>
% endif
