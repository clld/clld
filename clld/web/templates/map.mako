<% options = map.options() %>
% if options.get('sidebar'):
<div id="map-container">
    % if hasattr(map, 'legend'):
    ${map.legend()}
    % endif
    <div id="${map.eid}" style="position: relative; width: 100%; height: 200px;"> </div>
    <script>$(window).load(function() {${h.JS_CLLD.map(map.eid, dict((l.id, l.data) for l in map.layers), options)|n};});</script>
</div>
% else:
<div class="well well-small" id="map-container">
    <ul class="nav nav-pills">
        % for legend in map.legends:
        ${legend.render()|n}
        % endfor
        <li>
            <label class="checkbox inline" style="margin-left: 5px; margin-right: 5px;">
                <input id="map-label-visiblity" type="checkbox" class="inline" onclick='${h.JS_CLLD.mapToggleLabels(map.eid, h.JS("this"))|n}'>
                Show/hide Labels
            </label>
        </li>
    </ul>
    <div id="${map.eid}" style="width: 100%; height: 500px;"> </div>
    <script>
    $(window).load(function() {${h.JS_CLLD.map(map.eid, dict((l.id, l.data) for l in map.layers), options)|n};});
    $('.dropdown-menu .stay-open').click(function(e) {
        e.stopPropagation();
    });
    </script>
</div>
% endif
