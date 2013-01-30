
OpenLayers = {
    StyleMap: function(){},
    Projection: function(){},
    Map: function(){},
    Bounds: function(){},
    LonLat: function(){},
    Popup: {FramedCloud: function(){}},
    Control: {LayerSwitcher: function(){}, SelectFeature: function(){}},
    Format: {GeoJSON: function(){}},
    Strategy: {Fixed: function(){}},
    Protocol: {HTTP: function(){}},
    Layer: {Vector: function(){}}
}

google = {
    feeds: {
        Feed: function(){
            return {
                setNumEntries: function(){},
                load: function(){}
            }
        }
    }
}
