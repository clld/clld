<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>


<h2>${_('Languages')}</h2>
<p>
    ${_('Languages under analysis for this project')}
</p>

% if request.map:
${request.map.render()}
% endif

${ctx.render()}
