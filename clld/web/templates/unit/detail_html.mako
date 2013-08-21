<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "units" %>


<h2>${_('Unit')} ${ctx.name}</h2>

<p>
    ${ctx.description}
</p>

<dl>
% for key, objs in h.groupby(ctx.data, lambda o: o.key):
<dt>${key}</dt>
    % for obj in sorted(objs, key=lambda o: o.ord):
    <dd>${obj.value}</dd>
    % endfor
% endfor
</dl>

<h3>${_('Values')}</h3>
<dl>
    % for value in ctx.unitvalues:
    <dt>${h.link(request, value.unitparameter)}</dt>
    <dd>${h.link(request, value)}</dd>
    % endfor
</dl>
