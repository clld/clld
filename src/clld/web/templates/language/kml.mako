<?xml version="1.0" encoding="utf-8"?>
<kml xmlns="http://earth.google.com/kml/2.1"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <Document>
    <name>${getattr(context, 'name', _('Languages'))}</name>
      <description>
      </description>
    <open>1</open>
    <% objs = ctx.get_query(limit=3000) if getattr(ctx, 'get_query') else [ctx] %>
    % for obj in objs:
    <Style id="${obj.id}">
      <IconStyle>
        <Icon>
          <href>${h.map_marker_url(request, obj)}</href>
        </Icon>
      </IconStyle>
    </Style>
    <Placemark>
      <name>${obj.name}</name>
      <description>
        <![CDATA[
        ${h.link(request, obj)}
        ]]>
      </description>
      <Point><coordinates>${obj.longitude},${obj.latitude}</coordinates></Point>
        <styleUrl>#${obj.id}</styleUrl>
    </Placemark>
    % endfor
  </Document>
</kml>
