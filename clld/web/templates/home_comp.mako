<%inherit file="${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "dataset" %>

<%def name="contextnav()">
    % for name in request.registry.settings['home_comp']:
    ${util.contextnavitem(name)}
    % endfor
</%def>
${next.body()}
