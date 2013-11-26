import os

try:  # pragma: no cover
    from fabric.api import sudo, cd, run, get
    from fabric.contrib.files import exists
    import fabtools
except ImportError:  # pragma: no cover
    pass
from path import path

from clld.deploy.config import APPS
from clld.deploy.util import create_file_as_root


APP = APPS['solr']
SOLR_HOME = path('/opt/solr')
SOLR_DOWNLOAD = 'http://apache.openmirror.de/lucene/solr/4.5.1/solr-4.5.1.tgz'
#SOLR_DOWNLOAD = 'http://localhost/solr-4.5.1.tgz'

TOMCAT_SOLR_CONFIG = """\
<?xml version="1.0" encoding="utf-8"?>
<Context docBase="{0}/solr.war" debug="0" crossContext="true">
  <Environment name="solr/home" type="java.lang.String" value="{0}" override="true"/>
</Context>
""".format(SOLR_HOME)

here = path(__file__).dirname()
SCHEMA = here.joinpath('schema.xml')
SOLRCONFIG = here.joinpath('solrconfig.xml')


def _content(p):
    with open(p) as fp:
        c = fp.read()
    return c


def core_dir(name, *comps):  # pragma: no cover
    args = [name] + list(comps)
    return SOLR_HOME.joinpath(*args)


def data_dir(name=None):  # pragma: no cover
    args = ['data']
    if name:
        args.append(name)
    return SOLR_HOME.joinpath(*args)


def restart_tomcat(check_path=None, result='200 OK'):  # pragma: no cover
    fabtools.require.service.restarted('tomcat6')
    if check_path:
        res = run('curl -I http://localhost:8080/solr' + check_path)
        assert result in res


def require_solr():  # pragma: no cover
    fabtools.require.deb.package('tomcat6')
    fabtools.require.deb.package('curl')
    fabtools.require.deb.package('apache2-utils')
    fabtools.require.files.directory(SOLR_HOME, use_sudo=True, owner='root', group='root')
    fabtools.require.files.directory(data_dir(), use_sudo=True, owner='tomcat6')

    if not exists(SOLR_HOME.joinpath('solr.xml')):
        sudo('curl -o /tmp/solr.tgz %s' % SOLR_DOWNLOAD)
        with cd('/tmp'):
            sudo('tar -xzvf solr.tgz')
            sudo('cp -R solr-4.5.1/example/solr/* %s' % SOLR_HOME)
            # TODO:
            #cp solr-4.5.1/example/lib/ext/*.jar /usr/share/tomcat6/lib/
            sudo('cp solr-4.5.1/example/webapps/solr.war %s' % SOLR_HOME)
            sudo('rm -rf %s' % core_dir('collection1', 'conf', 'velocity'))
            sudo('rm -rf %s' % core_dir('collection1', 'conf', 'xslt'))
            sudo('rm -rf solr-4.5.1')
            sudo('rm solr.tgz')

    create_file_as_root(
        core_dir('collection1', 'conf', 'solrconfig.xml'),
        _content(SOLRCONFIG) % data_dir('collection1'))
    create_file_as_root(core_dir('collection1', 'conf', 'schema.xml'), _content(SCHEMA))

    #
    # TODO: proxy behind nginx with basic auth!
    # https://www.digitalocean.com/community/articles/how-to-create-a-ssl-certificate-on-nginx-for-ubuntu-12-04
    #
    #create_file_as_root(APP.nginx_location, '')
    create_file_as_root('/etc/tomcat6/Catalina/localhost/solr.xml', TOMCAT_SOLR_CONFIG)
    restart_tomcat(check_path='/admin/ping')


def require_core(name, schema=None):  # pragma: no cover
    if not exists(core_dir(name)):
        sudo('cp -R %s %s' % (core_dir('collection1'), core_dir(name)))

    create_file_as_root(
        core_dir(name, 'conf', 'solrconfig.xml'),
        _content(SOLRCONFIG) % data_dir(name))
    create_file_as_root(core_dir(name, 'conf', 'schema.xml'), _content(SCHEMA))

    create_file_as_root(core_dir(name, 'core.properties'), 'name=%s' % name)
    restart_tomcat(check_path='/%s/admin/ping' % name)


def drop_core(name):  # pragma: no cover
    sudo('rm -rf %s' % data_dir(name))
    sudo('rm -rf %s' % core_dir(name))
    restart_tomcat(check_path='/%s/admin/ping' % name, result='404 Not Found')
