<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "units" %>


<h2>${_('Unit')} ${ctx.name}</h2>

<dl>
% for k, v in ctx.datadict().items():
<dt>${k}</dt>
<dd>${v}</dd>
% endfor
</dl>

<ul>
% for c in ctx.counterparts:
<li>${h.link(request, c.valueset.parameter)} (${h.link(request, c.valueset.contribution)} Dictionary)</li>
% endfor
</ul>

<h3>${_('Values')}</h3>
<dl>
    % for value in ctx.unitvalues:
    <dt>${h.link(request, value.unitparameter)}</dt>
    <dd>${h.link(request, value)}</dd>
    % endfor
</dl>
