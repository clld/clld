<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>


<h2>${_('Language')} ${ctx.name}</h2>

<div>
    <% dt = request.registry.getUtility(h.interfaces.IDataTable, 'values'); dt = dt(request, h.models.Value, language=ctx) %>
    ${dt.render()}
</div>

<%def name="sidebar()">
    ${util.language_meta()}
</%def>
