<?xml version="1.0" encoding="utf-8"?>
<oai:OAI-PMH xmlns:atom="http://www.w3.org/2005/Atom"
         xmlns:olac="http://www.language-archives.org/OLAC/1.1/"
         xmlns:oai="http://www.openarchives.org/OAI/2.0/"
         xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
                             http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
    <%namespace name="olac_record" file="olac_record.mako"/>
    <%namespace name="olac_archive" file="olac_archive.mako"/>

<%def name="header(lang)">
  <oai:header>
    <oai:identifier>${cfg.format_identifier(request, lang)}</oai:identifier>
    <oai:datestamp>${date(lang.updated)}</oai:datestamp>
  </oai:header>
</%def>

<%def name="record(lang)">
  <oai:record>
    ${header(lang)}
    <oai:metadata>
      ${olac_record.record(lang)}
    </oai:metadata>
  </oai:record>
</%def>

  <oai:responseDate>${response_date}</oai:responseDate>
  <oai:request ${' '.join(k + '="' + v + '"' for k, v in params.items())|n}>${request.route_url('olac')}</oai:request>

  % if error:
  <oai:error code="${error[0]}">${error[1]}</oai:error>
  % else:
    % if verb == 'Identify':
    <oai:Identify>
      <oai:repositoryName>${request.dataset}</oai:repositoryName>
      <oai:baseURL>${request.route_url('olac')}</oai:baseURL>
      <oai:protocolVersion>2.0</oai:protocolVersion>
      <oai:adminEmail>${cfg.admin(request).email}</oai:adminEmail>
      <oai:earliestDatestamp>${date(earliest.updated)}</oai:earliestDatestamp>
      <oai:deletedRecord>no</oai:deletedRecord>
      <oai:granularity>YYYY-MM-DD</oai:granularity>
      <oai:description>
        <oai-identifier xmlns="http://www.openarchives.org/OAI/2.0/oai-identifier"
                xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai-identifier
                                    http://www.openarchives.org/OAI/2.0/oai-identifier.xsd">
          <scheme>${cfg.scheme}</scheme>
          <repositoryIdentifier>${request.dataset.domain}</repositoryIdentifier>
          <delimiter>${cfg.delimiter}</delimiter>
          <sampleIdentifier>${cfg.format_identifier(request, earliest)}</sampleIdentifier>
        </oai-identifier>
      </oai:description>
      <oai:description>
        ${olac_archive.archive()}
      </oai:description>
    </oai:Identify>
    % elif verb == 'GetRecord':
    <oai:GetRecord>
      ${record(language)}
    </oai:GetRecord>
    % elif verb == 'ListIdentifiers':
    <oai:ListIdentifiers>
      % for lang in languages:
        ${header(lang)}
      % endfor
      % if resumptionToken:
      <oai:resumptionToken>${resumptionToken}</oai:resumptionToken>
      % endif
    </oai:ListIdentifiers>
    % elif verb == 'ListRecords':
    <oai:ListRecords>
      % for lang in languages:
        ${record(lang)}
      % endfor
      % if resumptionToken:
      <oai:resumptionToken>${resumptionToken}</oai:resumptionToken>
      % endif
    </oai:ListRecords>
    % elif verb == 'ListMetadataFormats':
    <oai:ListMetadataFormats>
      <oai:metadataFormat>
        <oai:metadataPrefix>olac</oai:metadataPrefix>
        <oai:schema>http://www.language-archives.org/OLAC/1.1/olac.xsd</oai:schema>
        <oai:metadataNamespace>http://www.language-archives.org/OLAC/1.1/</oai:metadataNamespace>
      </oai:metadataFormat>
    </oai:ListMetadataFormats>
    % endif
  % endif
</oai:OAI-PMH>
