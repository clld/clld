<%def name="archive()">
  <olac-archive type="institutional"
                currentAsOf="${response_date.split('T')[0]}"
                xmlns="http://www.language-archives.org/OLAC/1.1/olac-archive"
                xsi:schemaLocation="http://www.language-archives.org/OLAC/1.1/olac-archive
                                    http://www.language-archives.org/OLAC/1.1/olac-archive.xsd">
    <% desc = cfg.description(request) %>
    <archiveURL>${desc['archiveURL']}/</archiveURL>
    % for p in desc['participants']:
    <participant name="${p.name}" role="${p.role}" email="${p.email}"/>
    % endfor
    <institution>${desc['institution'].name}</institution>
    <institutionURL>${desc['institution'].url}</institutionURL>
    <shortLocation>${desc['institution'].location}</shortLocation>
    <synopsis>${desc['synopsis']}</synopsis>
    <access>Open Access</access>
  </olac-archive>
</%def>
