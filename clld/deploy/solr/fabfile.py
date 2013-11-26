try:
    from fabric.api import task, run
except ImportError:  # pragma: no cover
    pass

from clld.deploy import solr


@task
def install():
    solr.require_solr()  # pragma: no cover


@task
def createcore(name):
    solr.require_core(name)  # pragma: no cover


@task
def dropcore(name):
    solr.drop_core(name)  # pragma: no cover


@task
def dropindex(name):
    for data in ['<delete><query>*:*</query></delete>', '<commit/>']:
        run("curl http://localhost:8080/solr/%s/update --data '%s' "
            "-H 'Content-type:text/xml; charset=utf-8'" % (name, data))
