<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Languages')}</%block>

<h2>${_('Languages')}</h2>

% if map_ or request.map:
${(map_ or request.map).render()}
% endif

${ctx.render()}
