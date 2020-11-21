% if obj.options.get('sidebar'):
<div id="map-container">
    % if hasattr(obj, 'legend'):
    ${obj.legend()}
    % endif
    <div id="${obj.eid}" style="position: relative; width: 100%; height: 200px;"> </div>
    <script>$(window).load(function() {${h.JS_CLLD.map(obj.eid, dict((l.id, l.data) for l in obj.layers), obj.options)|n};});</script>
</div>
% else:
<div class="well well-small" id="map-container">
    <ul class="nav nav-pills">
        % for legend in obj.legends:
        ${legend.render()|n}
        % endfor
        % if not obj.options.get('no_showlabels'):
        <li>
            <label class="checkbox inline" style="margin-left: 5px; margin-right: 5px;">
                <input id="map-label-visiblity" type="checkbox" ${'checked="checked"' if obj.options.get('show_labels') else ''|n}class="inline" onclick='${h.JS_CLLD.mapToggleLabels(obj.eid, h.JS("this"))|n}'>
                ${_('Show/hide Labels')}
            </label>
        </li>
        % endif
    </ul>
    <div id="${obj.eid}" style="width: 100%; height: ${obj.options.get('height', 500)}px;"> </div>
    <script>
    $(window).load(function() {
        ${h.JS_CLLD.map(obj.eid, dict((l.id, l.data) for l in obj.layers), obj.options)|n};
    });
    $('.dropdown-menu .stay-open').click(function(e) {
        e.stopPropagation();
    });
    </script>
</div>
% endif
