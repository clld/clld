from fabric.api import task

from clld.deploy import solr


@task
def install():
    solr.require_solr()


@task
def createcore(name):
    solr.require_core(name)


@task
def dropcore(name):
    solr.drop_core(name)
