<%inherit file="apics.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "home" %>

<%def name="contextnav()">
    ${util.contextnavitem('legal')}
    ##${util.contextnavitem('download')}
</%def>
${next.body()}
