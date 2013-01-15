<%namespace name="util" file="../util.mako"/>



<div id="map_canvas_${ctx.id}" style="width:300px; height:200px">
    <h2>stuff</h2>
</div>
##
## TODO: check out openlayers instead of gmaps
##
<script>
    $(function (){
        var mapOptions = {
          center: new google.maps.LatLng(${ctx.latitude}, ${ctx.longitude}),
          zoom: 2,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map(document.getElementById("map_canvas_${ctx.id}"), mapOptions);
        //var ctaLayer = new google.maps.KmlLayer('${request.route_url("language_alt", id=ctx.id, ext="kml")}', {map: map});


        var bounds = new google.maps.LatLngBounds();

        var parser = new geoXML3.parser({map: map});
        parser.parse('${request.route_url("language_alt", id=ctx.id, ext="kml")}');

        var parser = new geoXML3.parser({
            map: map,
            processStyles: true,
            createMarker: addMyMarker,
            //createOverlay: addMyOverlay
        });
        parser.parse('${request.route_url("language_alt", id=ctx.id, ext="kml")}');
        //parser.parse('${request.route_url("languages_alt", ext="kml")}');

        function addMyMarker(placemark) {
            //alert(placemark.styleUrl);
            //alert(placemark.extendedData);
            // Marker handling code goes here
            //bounds.extend(new google.maps.LatLng(placemark.latitude, placemark.longitude))
            if (1) {
                parser.createMarker(placemark);
            }
        };

        // extend bounds with each point

        //map.fitBounds(bounds); 
        var listener = google.maps.event.addListenerOnce(map, "idle", function() { 
            if (map.getZoom() > 7) {
                map.setZoom(7);
            }
        });

/*
http://www.geocodezip.com/geoxml3_test/geoxml3_test.html

*/
    });
</script>
