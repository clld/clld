<%inherit file="${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "dataset" %>

<%def name="contextnav()">
    ${util.contextnavitem('legal')}
    ##${util.contextnavitem('download')}
</%def>
${next.body()}
