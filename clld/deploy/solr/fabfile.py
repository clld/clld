try:
    from fabric.api import task
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
