<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>

##<%def name="sidebar()">
##    sidebar
##</%def>

<%block name="contextnav">
    ${util.contextnav((h.tag('a', 'Home', href=request.route_url('home')), True))}
</%block>

<h2>${_('Languages')}</h2>
<p>
    ${_('Languages under analysis for this project')}
</p>

##
## TODO: lookup whether any map is registered for this view, and if so, render it!
##
% if request.map:
${request.map.render()}
% endif

${ctx.render()}
