<?xml version="1.0" encoding="utf-8"?>
<kml xmlns="http://earth.google.com/kml/2.1"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:wals="http://wals.info/terms#">
  <Document>
    <name>Mako: ${getattr(context, 'name', _('Languages'))}</name>
      <description>
	Language
      </description>
    <open>1</open>
    <% objs = ctx.get_query(limit=3000) if getattr(ctx, 'get_query') else [ctx] %>
    % for obj in objs:
    <Style id="${obj.id}">
      <IconStyle>
        <Icon>
          <href>http://chart.googleapis.com/chart?cht=p&amp;chs=38x38&amp;chd=t:60,40&amp;chco=FF0000|00FF00&amp;chf=bg,s,FFFFFF00</href>
        </Icon>
      </IconStyle>
    </Style>
    <Placemark>
      <name>${obj.name}</name>
      <description>
      </description>
      <Point><coordinates>${obj.longitude},${obj.latitude}</coordinates></Point>
        <ExtendedData>
          <wals:code>${obj.id}</wals:code>
        </ExtendedData>
	<styleUrl>#${obj.id}</styleUrl>
    </Placemark>
    % endfor
  </Document>
</kml>