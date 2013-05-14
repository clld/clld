<% options = map.options() %>
% if options.get('sidebar'):
<div>
    % if hasattr(map, 'legend'):
    ${map.legend()}
    % endif
    <div id="${map.eid}" style="position: relative; width: 100%; height: 200px;"> </div>
    <script>$(window).load(function() {${h.JSMap.init(map.eid, dict((l.id, l.data) for l in map.layers), options)|n};});</script>
</div>
% else:
<div class="well well-small" id="map-container">
    <ul class="nav nav-pills">
    % if len(map.layers) > 1:
        <li class="dropdown">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#">
                Layers
                <b class="caret"></b>
            </a>
            <ul class="dropdown-menu">
            % for layer in map.layers:
                <li>
                    <label class="checkbox inline" style="margin-left: 5px; margin-right: 5px;">
                        <input type="checkbox" checked="checked" onclick='${h.JSMap.toggleLayer(layer.id, h.JS("this"))|n}'>
                        % if hasattr(layer, 'marker'):
                        ${layer.marker}
                        % endif
                        ${layer.name}
                    </label>
                </li>
            % endfor
            </ul>
        </li>
    % endif
    % if hasattr(map, 'legend'):
        <% legend = map.legend() %>
        <% if not isinstance(legend, (tuple, list)): legend = [legend] %>
        % for l in legend:
            ${l}
        % endfor
    % endif
        <li>
            <label class="checkbox inline" style="margin-left: 5px; margin-right: 5px;">
                <input type="checkbox" onclick='${h.JSMap.toggleLabels(h.JS("this"))|n}'>
                Show/hide Labels
            </label>
        </li>
    </ul>
    <div id="${map.eid}" style="width: 100%; height: 500px;"> </div>
    <script>
    $(window).load(function() {${h.JSMap.init(map.eid, dict((l.id, l.data) for l in map.layers), options)|n};});
    $('.dropdown-menu .stay-open').click(function(e) {
        e.stopPropagation();
    });
    </script>
</div>
% endif
