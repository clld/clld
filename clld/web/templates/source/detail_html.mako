<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sources" %>


<h2>${_('Source')} ${ctx.name}</h2>

<ol>
% for k, v in ctx.datadict().items():
<dt>${k}</dt>
<dd>${v}</dd>
% endfor
</ol>

<%def name="sidebar()">
% if ctx.languagesource:
<%util:well title="${_('Languages')}">
    <ul class="nav nav-pills nav-stacked">
    % for source_assoc in ctx.languagesource:
        <li>${h.link(request, source_assoc.language)}</li>
    % endfor
    </ul>
</%util:well>
% endif
</%def>
