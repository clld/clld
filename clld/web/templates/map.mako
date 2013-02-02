<div class="accordion" id="map-container">
    <div class="accordion-group">
        <div class="accordion-heading">
            <a class="accordion-toggle" data-toggle="collapse" data-parent="#map-container" href="#map-inner">
                show/hide map
            </a>
        </div>
        <div id="map-inner" class="accordion-body collapse in">
            <div class="accordion-inner">
		% if len(map.layers) > 1:
	        <ul class="nav nav-pills">
		    <li class="dropdown">
			<a class="dropdown-toggle" data-toggle="dropdown" href="#">
			    Layers
			    <b class="caret"></b>
			</a>
			<ul class="dropdown-menu">
			% for layer in map.layers:
			    <li onclick="CLLD.Map.toggleLayer('${layer["name"]}', this.firstElementChild.firstElementChild);">
			        <label class="checkbox inline" style="margin-left: 5px; margin-right: 5px;">
				    <input type="checkbox" checked="checked">
				    % if 'marker' in layer:
				    ${layer['marker']}
				    % endif
				    ${layer["name"]}
				</label>
			    </li>
			% endfor
			</ul>
		    </li>
		</ul>
		% endif
		% if hasattr(map, 'legend'):
		${map.legend()}
		% endif
		<div id="${map.eid}" style="width: 100%; height: 500px;"> </div>
		<script>
$(window).load(function() {
    CLLD.Map.init(${h.dumps(map.layers)|n}, ${h.dumps(map.options())|n});
});
		</script>
            </div>
        </div>
    </div>
</div>
