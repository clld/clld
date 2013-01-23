<div class="accordion" id="map-container">
    <div class="accordion-group">
        <div class="accordion-heading">
            <a class="accordion-toggle" data-toggle="collapse" data-parent="#map-container" href="#map-inner">
                show/hide map
            </a>
        </div>
        <div id="map-inner" class="accordion-body collapse in">
            <div class="accordion-inner">
	        <ul class="nav nav-pills">
		    <li class="dropdown">
			<a class="dropdown-toggle" data-toggle="dropdown" href="#">
			    Values
			    <b class="caret"></b>
			</a>
			<ul class="dropdown-menu">
			% for name, url in map.layers():
			    <li onclick="CLLD.Map.toggleLayer('${name}', this.firstElementChild.firstElementChild);">
			        <label class="checkbox inline" style="margin-left: 5px; margin-right: 5px;">
				    <input type="checkbox" checked="checked">
				    ##
				    ## TODO: creation of legend must be pluggable!
				    ##

				    ##<img src="${request.static_url('wals3:static/icons/'+de.icon_id+'.png')}">
				    ${name}
				</label>
			    </li>
			% endfor
			</ul>
		    </li>
		</ul>
		<div id="${map.eid}" style="width: 100%; height: 400px;"> </div>
		<script>
$(window).load(function() {
    CLLD.Map.init(${h.dumps(map.layers())|n});
});
		</script>
            </div>
        </div>
    </div>
</div>
