<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>


<h2>${_('Examples')}</h2>
<p>
    ${_('Examples for this project')}
</p>
<div>
    ${ctx.render()}
</div>
