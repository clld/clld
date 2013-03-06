import os
from tempfile import mktemp

from clld import PY3
if PY3:
    print('fabric requires python2.x')
else:
    from fabric.api import sudo, cd, run, get
    from fabric.contrib.files import exists
    import fabtools
from path import path

from clld.deploy.config import APPS
from clld.deploy.util import create_file_as_root


APP = APPS['solr']
SOLR_HOME = path('/opt/solr')
SOLR_DOWNLOAD = 'http://apache.openmirror.de/lucene/solr/4.1.0/solr-4.1.0.tgz'
#SOLR_DOWNLOAD = 'http://localhost/solr-4.1.0.tgz'

TOMCAT_SOLR_CONFIG = """\
<?xml version="1.0" encoding="utf-8"?>
<Context docBase="{0}/solr.war" debug="0" crossContext="true">
  <Environment name="solr/home" type="java.lang.String" value="{0}" override="true"/>
</Context>
""".format(SOLR_HOME)

CORE_CONFIG_TEMPLATE = '<core name="{0}" instanceDir="{0}" />\n'


def core_dir(name, *comps):
    args = [name] + list(comps)
    return SOLR_HOME.joinpath(*args)


def data_dir(name=None):
    args = ['data']
    if name:
        args.append(name)
    return SOLR_HOME.joinpath(*args)


def restart_tomcat(check_path=None, result='200 OK'):
    fabtools.require.service.restarted('tomcat6')
    if check_path:
        res = run('curl -I http://localhost:8080/solr' + check_path)
        assert result in res


def update_config(updater):
    solr_xml_tmp = mktemp()
    get(SOLR_HOME.joinpath('solr.xml'), solr_xml_tmp)
    with open(solr_xml_tmp) as fp:
        contents = fp.read()
    create_file_as_root(SOLR_HOME.joinpath('solr.xml'), updater(contents))
    os.remove(solr_xml_tmp)


def require_solr():
    fabtools.require.deb.package('tomcat6')
    fabtools.require.deb.package('curl')
    fabtools.require.deb.package('apache2-utils')
    fabtools.require.files.directory(SOLR_HOME, use_sudo=True, owner='root', group='root')
    fabtools.require.files.directory(data_dir(), use_sudo=True, owner='tomcat6')

    if not exists(SOLR_HOME.joinpath('solr.xml')):
        sudo('curl -o /tmp/solr.tgz %s' % SOLR_DOWNLOAD)
        with cd('/tmp'):
            sudo('tar -xzvf solr.tgz')
            sudo('cp -R solr-4.1.0/example/solr/* %s' % SOLR_HOME)
            sudo('cp solr-4.1.0/example/webapps/solr.war %s' % SOLR_HOME)
            sudo('rm -rf %s' % core_dir('collection1', 'conf', 'velocity'))
            sudo('rm -rf %s' % core_dir('collection1', 'conf', 'xslt'))
            sudo('rm -rf solr-4.1.0')
            sudo('rm solr.tgz')

    create_file_as_root(
        core_dir('collection1', 'conf', 'solrconfig.xml'),
        SOLR_CORE_CONFIG_TEMPLATE % data_dir('collection1'))

    #
    # TODO: proxy behind nginx with basic auth!
    #
    #create_file_as_root(APP.nginx_location, '')
    create_file_as_root('/etc/tomcat6/Catalina/localhost/solr.xml', TOMCAT_SOLR_CONFIG)
    restart_tomcat(check_path='/admin/ping')


def require_core(name, schema=None):
    if not exists(core_dir(name)):
        sudo('cp -R %s %s' % (core_dir('collection1'), core_dir(name)))

    create_file_as_root(
        core_dir(name, 'conf', 'solrconfig.xml'),
        SOLR_CORE_CONFIG_TEMPLATE % data_dir(name))
    #
    # TODO:
    # - require schema
    #
    update_config(updater=lambda c: c.replace('</cores>', CORE_CONFIG_TEMPLATE.format(name) + '</cores>'))
    restart_tomcat(check_path='/%s/admin/ping' % name)


def drop_core(name):
    sudo('rm -rf %s' % data_dir(name))
    sudo('rm -rf %s' % core_dir(name))
    update_config(updater=lambda c: c.replace(CORE_CONFIG_TEMPLATE.format(name), ''))
    restart_tomcat(check_path='/%s/admin/ping' % name, result='404 Not Found')


SOLR_CORE_CONFIG_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8" ?>
<config>
  <luceneMatchVersion>LUCENE_41</luceneMatchVersion>
  <dataDir>${solr.data.dir:%s}</dataDir>
  <directoryFactory name="DirectoryFactory"
                    class="${solr.directoryFactory:solr.NRTCachingDirectoryFactory}"/>

  <indexConfig>
  </indexConfig>

  <jmx />
  <updateHandler class="solr.DirectUpdateHandler2">
    <updateLog>
      <str name="dir">${solr.ulog.dir:}</str>
    </updateLog>
     <autoCommit>
       <maxTime>15000</maxTime>
       <openSearcher>false</openSearcher>
     </autoCommit>
  </updateHandler>
  <query>
    <maxBooleanClauses>1024</maxBooleanClauses>
    <filterCache class="solr.FastLRUCache"
                 size="512"
                 initialSize="512"
                 autowarmCount="0"/>
    <queryResultCache class="solr.LRUCache"
                     size="512"
                     initialSize="512"
                     autowarmCount="0"/>
    <documentCache class="solr.LRUCache"
                   size="512"
                   initialSize="512"
                   autowarmCount="0"/>
    <enableLazyFieldLoading>true</enableLazyFieldLoading>
   <queryResultWindowSize>20</queryResultWindowSize>
   <queryResultMaxDocsCached>200</queryResultMaxDocsCached>
    <listener event="newSearcher" class="solr.QuerySenderListener">
      <arr name="queries">
      </arr>
    </listener>
    <listener event="firstSearcher" class="solr.QuerySenderListener">
      <arr name="queries">
        <lst>
          <str name="q">static firstSearcher warming in solrconfig.xml</str>
        </lst>
      </arr>
    </listener>
    <useColdSearcher>false</useColdSearcher>
    <maxWarmingSearchers>2</maxWarmingSearchers>
  </query>
  <requestDispatcher handleSelect="false" >
    <requestParsers enableRemoteStreaming="true"
                    multipartUploadLimitInKB="2048000"
                    formdataUploadLimitInKB="2048"/>
    <httpCaching never304="true" />
  </requestDispatcher>
  <requestHandler name="/select" class="solr.SearchHandler">
     <lst name="defaults">
       <str name="echoParams">explicit</str>
       <int name="rows">10</int>
       <str name="df">text</str>
     </lst>
    </requestHandler>
  <requestHandler name="/query" class="solr.SearchHandler">
     <lst name="defaults">
       <str name="echoParams">explicit</str>
       <str name="wt">json</str>
       <str name="indent">true</str>
       <str name="df">text</str>
     </lst>
  </requestHandler>
  <requestHandler name="/get" class="solr.RealTimeGetHandler">
     <lst name="defaults">
       <str name="omitHeader">true</str>
       <str name="wt">json</str>
       <str name="indent">true</str>
     </lst>
  </requestHandler>
  <requestHandler name="/update" class="solr.UpdateRequestHandler">
  </requestHandler>
  <requestHandler name="/update/json" class="solr.JsonUpdateRequestHandler">
        <lst name="defaults">
         <str name="stream.contentType">application/json</str>
       </lst>
  </requestHandler>
  <requestHandler name="/update/csv" class="solr.CSVRequestHandler">
        <lst name="defaults">
         <str name="stream.contentType">application/csv</str>
       </lst>
  </requestHandler>
  <requestHandler name="/update/extract"
                  startup="lazy"
                  class="solr.extraction.ExtractingRequestHandler" >
    <lst name="defaults">
      <str name="lowernames">true</str>
      <str name="uprefix">ignored_</str>

      <!-- capture link hrefs but ignore div attributes -->
      <str name="captureAttr">true</str>
      <str name="fmap.a">links</str>
      <str name="fmap.div">ignored_</str>
    </lst>
  </requestHandler>
  <requestHandler name="/analysis/field"
                  startup="lazy"
                  class="solr.FieldAnalysisRequestHandler" />
  <requestHandler name="/analysis/document"
                  class="solr.DocumentAnalysisRequestHandler"
                  startup="lazy" />
  <requestHandler name="/admin/"
                  class="solr.admin.AdminHandlers" />
  <requestHandler name="/admin/ping" class="solr.PingRequestHandler">
    <lst name="invariants">
      <str name="q">solrpingquery</str>
    </lst>
    <lst name="defaults">
      <str name="echoParams">all</str>
    </lst>
  </requestHandler>
  <requestHandler name="/debug/dump" class="solr.DumpRequestHandler" >
    <lst name="defaults">
     <str name="echoParams">explicit</str>
     <str name="echoHandler">true</str>
    </lst>
  </requestHandler>
  <requestHandler name="/replication" class="solr.ReplicationHandler" >
  </requestHandler>
  <searchComponent name="spellcheck" class="solr.SpellCheckComponent">
    <str name="queryAnalyzerFieldType">textSpell</str>
    <lst name="spellchecker">
      <str name="name">default</str>
      <str name="field">name</str>
      <str name="classname">solr.DirectSolrSpellChecker</str>
      <str name="distanceMeasure">internal</str>
      <float name="accuracy">0.5</float>
      <int name="maxEdits">2</int>
      <int name="minPrefix">1</int>
      <int name="maxInspections">5</int>
      <int name="minQueryLength">4</int>
      <float name="maxQueryFrequency">0.01</float>
    </lst>
    <lst name="spellchecker">
      <str name="name">wordbreak</str>
      <str name="classname">solr.WordBreakSolrSpellChecker</str>
      <str name="field">name</str>
      <str name="combineWords">true</str>
      <str name="breakWords">true</str>
      <int name="maxChanges">10</int>
    </lst>
  </searchComponent>
  <requestHandler name="/spell" class="solr.SearchHandler" startup="lazy">
    <lst name="defaults">
      <str name="df">text</str>
      <str name="spellcheck.dictionary">default</str>
      <str name="spellcheck.dictionary">wordbreak</str>
      <str name="spellcheck">on</str>
      <str name="spellcheck.extendedResults">true</str>
      <str name="spellcheck.count">10</str>
      <str name="spellcheck.alternativeTermCount">5</str>
      <str name="spellcheck.maxResultsForSuggest">5</str>
      <str name="spellcheck.collate">true</str>
      <str name="spellcheck.collateExtendedResults">true</str>
      <str name="spellcheck.maxCollationTries">10</str>
      <str name="spellcheck.maxCollations">5</str>
    </lst>
    <arr name="last-components">
      <str>spellcheck</str>
    </arr>
  </requestHandler>
  <searchComponent name="tvComponent" class="solr.TermVectorComponent"/>
  <searchComponent name="terms" class="solr.TermsComponent"/>
  <requestHandler name="/terms" class="solr.SearchHandler" startup="lazy">
     <lst name="defaults">
      <bool name="terms">true</bool>
      <bool name="distrib">false</bool>
    </lst>
    <arr name="components">
      <str>terms</str>
    </arr>
  </requestHandler>
  <searchComponent class="solr.HighlightComponent" name="highlight">
    <highlighting>
      <fragmenter name="gap"
                  default="true"
                  class="solr.highlight.GapFragmenter">
        <lst name="defaults">
          <int name="hl.fragsize">100</int>
        </lst>
      </fragmenter>
      <fragmenter name="regex"
                  class="solr.highlight.RegexFragmenter">
        <lst name="defaults">
          <int name="hl.fragsize">70</int>
          <float name="hl.regex.slop">0.5</float>
          <str name="hl.regex.pattern">[-\w ,/\n\&quot;&apos;]{20,200}</str>
        </lst>
      </fragmenter>
      <formatter name="html"
                 default="true"
                 class="solr.highlight.HtmlFormatter">
        <lst name="defaults">
          <str name="hl.simple.pre"><![CDATA[<em>]]></str>
          <str name="hl.simple.post"><![CDATA[</em>]]></str>
        </lst>
      </formatter>
      <encoder name="html"
               class="solr.highlight.HtmlEncoder" />
      <fragListBuilder name="simple"
                       class="solr.highlight.SimpleFragListBuilder"/>
      <fragListBuilder name="single"
                       class="solr.highlight.SingleFragListBuilder"/>
      <fragListBuilder name="weighted"
                       default="true"
                       class="solr.highlight.WeightedFragListBuilder"/>
      <fragmentsBuilder name="default"
                        default="true"
                        class="solr.highlight.ScoreOrderFragmentsBuilder">
      </fragmentsBuilder>
      <fragmentsBuilder name="colored"
                        class="solr.highlight.ScoreOrderFragmentsBuilder">
        <lst name="defaults">
          <str name="hl.tag.pre"><![CDATA[
               <b style="background:yellow">,<b style="background:lawgreen">,
               <b style="background:aquamarine">,<b style="background:magenta">,
               <b style="background:palegreen">,<b style="background:coral">,
               <b style="background:wheat">,<b style="background:khaki">,
               <b style="background:lime">,<b style="background:deepskyblue">]]>
</str>
          <str name="hl.tag.post"><![CDATA[</b>]]></str>
        </lst>
      </fragmentsBuilder>
      <boundaryScanner name="default"
                       default="true"
                       class="solr.highlight.SimpleBoundaryScanner">
        <lst name="defaults">
          <str name="hl.bs.maxScan">10</str>
          <str name="hl.bs.chars">.,!? &#9;&#10;&#13;</str>
        </lst>
      </boundaryScanner>
      <boundaryScanner name="breakIterator"
                       class="solr.highlight.BreakIteratorBoundaryScanner">
        <lst name="defaults">
          <str name="hl.bs.type">WORD</str>
          <str name="hl.bs.language">en</str>
          <str name="hl.bs.country">US</str>
        </lst>
      </boundaryScanner>
    </highlighting>
  </searchComponent>
  <queryResponseWriter name="json" class="solr.JSONResponseWriter">
  </queryResponseWriter>
  <admin>
    <defaultQuery>*:*</defaultQuery>
  </admin>
</config>
"""
