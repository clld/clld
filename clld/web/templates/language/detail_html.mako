<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>


<h2>${_('Language')} ${ctx.name}</h2>

<div>
    <% dt = request.registry.getUtility(h.interfaces.IDataTable, 'values'); dt = dt(request, h.models.Value, language=ctx) %>
    ${dt.render()}
</div>

<%def name="sidebar()">
    % if request.map:
    ${request.map.render()}
    % endif
</%def>

<%def name="sidebar()">
    <div class="accordion" id="sidebar-accordion">
        % if request.map:
        <%util:accordion_group eid="acc-map" parent="sidebar-accordion" title="Map" open="${True}">
            ${request.map.render()}
            <p>Coordinates: ${ctx.latitude}, ${ctx.longitude}</p>
        </%util:accordion_group>
        % endif
        % if ctx.sources:
        <%util:accordion_group eid="sources" parent="sidebar-accordion" title="Sources">
            <ul>
                % for source in ctx.sources:
                <li>${h.link(request, source, label=source.description)}<br />
                <small>${h.link(request, source)}</small></li>
                % endfor
            </ul>
        </%util:accordion_group>
        % endif
        <%util:accordion_group eid="acc-names" parent="sidebar-accordion" title="Alternative names">
            <dl>
            % for type_, identifiers in h.groupby(sorted(ctx.identifiers, key=lambda i: i.type), lambda j: j.type):
                <dt>${type_}:</dt>
                % for identifier in identifiers:
                <dd>${h.language_identifier(request, identifier)}</dd>
                % endfor
            % endfor
            </dl>
        </%util:accordion_group>
    </div>
</%def>
