"""
fabric tasks
------------

We use the following mechanism to provide common task implementations for all clld apps:
This module defines and exports tasks which are run on localhost and take a first argument
"environment". The environment is used to determine the correct host to run the actual
task on. To connect tasks to a certain app, the app's fabfile needs to import this module
and run the init function, passing an app name defined in the global clld app config.
"""
from fabric.api import task, hosts, execute, env

from clld.deploy import config
from clld.deploy import util
from clld.deploy import varnish


APP = None


def init(app_name):
    global APP
    APP = config.APPS[app_name]


def _assign_host(environment):
    assert environment in ['production', 'test']
    env.hosts = [getattr(APP, environment)]


@task
def bootstrap():
    util.bootstrap()  # pragma: no cover


@hosts('localhost')
@task
def stop(environment):
    """stop app by changing the supervisord config
    """
    _assign_host(environment)
    execute(util.supervisor, APP, 'pause')


@hosts('localhost')
@task
def start(environment):
    """start app by changing the supervisord config
    """
    _assign_host(environment)
    execute(util.supervisor, APP, 'run')


@hosts('localhost')
@task
def cache():
    """
    """
    _assign_host('production')
    execute(varnish.cache, APP)


@hosts('localhost')
@task
def uncache():
    """
    """
    _assign_host('production')
    execute(varnish.uncache, APP)


@hosts('localhost')
@task
def maintenance(environment, hours=2):
    """create a maintenance page giving a date when we expect the service will be back

    :param hours: Number of hours we expect the downtime to last.
    """
    _assign_host(environment)
    execute(util.maintenance, APP, hours=hours)


@hosts('localhost')
@task
def deploy(environment, with_blog=False):
    """deploy the app
    """
    _assign_host(environment)
    if not with_blog:
        with_blog = getattr(APP, 'with_blog', False)
    execute(util.deploy, APP, environment, with_blog=with_blog)


@hosts('localhost')
@task
def create_downloads(environment):
    """create all configured downloads
    """
    _assign_host(environment)
    execute(util.create_downloads, APP)


@hosts('localhost')
@task
def copy_files(environment):
    """copy files for the app
    """
    _assign_host(environment)
    execute(util.copy_files, APP)


@hosts('localhost')
@task
def run_script(environment, script_name, *args):
    """
    """
    _assign_host(environment)
    execute(util.run_script, APP, script_name, *args)
