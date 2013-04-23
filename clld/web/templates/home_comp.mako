<%inherit file="apics.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "home" %>

<%def name="contextnav()">
    ${util.contextnavitem('legal')}
</%def>
${next.body()}
