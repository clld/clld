<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>



<h2>${_('Value')} ${ctx.domainelement.name if ctx.domainelement else ctx.name}</h2>

<dl>
    <dt>Language:</dt>
    <dd>${h.link(request, ctx.language)}</dd>
    <dt>Parameter:</dt>
    <dd>${h.link(request, ctx.parameter)}</dd>
    % for k, v in ctx.datadict().items():
    <dt>${k}</dt>
    <dd>${v}</dd>
    % endfor
</dl>
