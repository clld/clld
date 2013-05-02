<%def name="record(lang)">
  <olac:olac xmlns:olac="http://www.language-archives.org/OLAC/1.1/"
           xmlns:dc="http://purl.org/dc/elements/1.1/"
           xmlns:dcterms="http://purl.org/dc/terms/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://www.language-archives.org/OLAC/1.1/ http://www.language-archives.org/OLAC/1.1/olac.xsd">
    <dc:title>${request.pub.get('sitetitle_short', request.pub.get('sitetitle', 'clld'))} Resources for ${lang.name}</dc:title>

    ##<dc:contributor xsi:type="olac:role" olac:code="editor" py:for="contrib in c.contribs">${contrib}</dc:contributor>

    <dc:description>
      A page listing all resources in ${request.pub.get('sitetitle_short', request.pub.get('sitetitle', 'clld'))} which are relevant to the language ${lang.name}.
    </dc:description>
    <dc:publisher>${request.pub.get('publisher', '')}</dc:publisher>
    <dc:language xsi:type="olac:language" olac:code="eng"/>
    % for code in cfg.iso_codes(lang):
    <dc:subject xsi:type="olac:language" olac:code="${code}"/>
    % endfor
    <dc:type xsi:type="olac:linguistic-type" olac:code="language_description"/>
    <dc:date>${date(lang.updated)}</dc:date>
    <dc:identifier xsi:type="dcterms:URI">${request.resource_url(lang)}</dc:identifier>
    <dc:type xsi:type="dcterms:DCMIType">Text</dc:type>
    <dc:format xsi:type="dcterms:IMT">text/html</dc:format>
  </olac:olac>
</%def>
