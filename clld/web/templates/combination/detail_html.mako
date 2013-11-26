<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Combination')} ${ctx.name}</%block>

<h2>${_('Combination')} ${ctx.name}</h2>

% if request.map:
${request.map.render()}
% endif
