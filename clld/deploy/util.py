"""
Deployment utilities for clld apps
"""
# flake8: noqa
#
# TODO: logrotate!
#
import time
import json
import crypt
import random
from getpass import getpass
import os
from datetime import datetime, timedelta
from importlib import import_module

from pytz import timezone, utc

try:  # pragma: no cover
    from fabric.api import sudo, run, local, put, env, cd, task, execute
    env.use_ssh_config = True
    from fabric.contrib.console import confirm
    from fabric.contrib.files import exists
    from fabtools import require
    require.python.DEFAULT_PIP_VERSION = None
    from fabtools.python import virtualenv
    from fabtools import service
    from fabtools import postgres
except ImportError:  # pragma: no cover
    sudo, run, local, put, env, cd, confirm, require, virtualenv, service, postgres = \
        None, None, None, None, None, None, None, None, None, None, None

from clld.deploy import config
from clld.scripts.util import data_file


# we prevent the tasks defined here from showing up in fab --list, because we only
# want the wrapped version imported from clld.deploy.tasks to be listed.
__all__ = []

DEFAULT_SITE = """\
server {
        listen 80 default_server;
        root /usr/share/nginx/www;
        index index.html index.htm;
        server_name localhost;

        location / {
                try_files $uri $uri/ /index.html;
        }

        location /asjp {
                rewrite ^/(.*) http://cldbs.eva.mpg.de/$1 permanent;
        }

        include /etc/nginx/locations.d/*.conf;
}
"""

LOCATION_TEMPLATE = """\
location /{app.name} {{
{auth}
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Forwarded-For  $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_connect_timeout 10;
        proxy_read_timeout 10;
        proxy_pass http://127.0.0.1:{app.port}/;
}}

location /{app.name}/admin {{
{admin_auth}
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Forwarded-For  $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_connect_timeout 10;
        proxy_read_timeout 10;
        proxy_pass http://127.0.0.1:{app.port}/admin;
}}

location /{app.name}/clld-static/ {{
        alias {app.venv}/src/clld/clld/web/static/;
}}

location /{app.name}/static/ {{
        alias {app.venv}/src/{app.name}/{app.name}/static/;
}}
"""

SITE_TEMPLATE = """\
server {{
    server_name  www.{app.domain};
    return       301 http://{app.domain}$request_uri;
}}

server {{
    server_name {app.domain};
    access_log /var/log/{app.name}/access.log;

    root {app.www};

    location / {{
{auth}
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Forwarded-For  $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_connect_timeout 10;
            proxy_read_timeout 10;
            proxy_pass http://127.0.0.1:{app.port}/;
    }}

    location /admin {{
{admin_auth}
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Forwarded-For  $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_connect_timeout 10;
            proxy_read_timeout 10;
            proxy_pass http://127.0.0.1:{app.port}/admin;
    }}

    location /clld-static/ {{
            alias {app.venv}/src/clld/clld/web/static/;
    }}

    location /static/ {{
            alias {app.venv}/src/{app.name}/{app.name}/static/;
    }}

    location /files/ {{
            alias {app.www}/files/;
    }}

    error_page 502 503 =502 /503.html;
    location = /503.html {{
        root {app.www};
    }}
}}
"""

LOGROTATE_TEMPLATE = """\
/var/log/{app.name}/access.log {{
        daily
        missingok
        rotate 52
        compress
        delaycompress
        notifempty
        create 0640 www-data adm
        sharedscripts
        prerotate
                if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
                        run-parts /etc/logrotate.d/httpd-prerotate; \
                fi; \
        endscript
        postrotate
                [ ! -f /var/run/nginx.pid ] || kill -USR1 `cat /var/run/nginx.pid`
        endscript
}}
"""

HTTP_503_TEMPLATE = """\
<html>
    <head>
        <title>Service Unavailable</title>
    </head>
<body>
<h1>{app.name} is currently down for maintenance</h1>
<p>We expect to be back around {timestamp}. Thanks for your patience.</p>
</body>
</html>
"""

_SUPERVISOR_TEMPLATE = """\
[program:{app.name}]
command={newrelic} run-program {gunicorn} -u {app.name} -g {app.name} --max-requests 1000 --limit-request-line 8000 --error-logfile {app.error_log} {app.config}
environment=NEW_RELIC_CONFIG_FILE="{app.newrelic_config}"
autostart=%s
autorestart=%s
redirect_stderr=True
"""
SUPERVISOR_TEMPLATE = {
    'pause': _SUPERVISOR_TEMPLATE % ('false', 'false'),
    'run': _SUPERVISOR_TEMPLATE % ('true', 'true'),
}

NEWRELIC_TEMPLATE = """\
[newrelic]
license_key = {newrelic_api_key}
app_name = {app.name}
monitor_mode = {monitor_mode}
log_file = {app.newrelic_log}
log_level = warning
ssl = false
capture_params = true
transaction_tracer.enabled = true
transaction_tracer.transaction_threshold = apdex_f
transaction_tracer.record_sql = raw
transaction_tracer.stack_trace_threshold = 0.5
transaction_tracer.explain_enabled = true
transaction_tracer.explain_threshold = 0.5
transaction_tracer.function_trace =
error_collector.enabled = true
error_collector.ignore_errors =
browser_monitoring.auto_instrument = false
thread_profiler.enabled = false
"""

_CONFIG_TEMPLATE = """\
[app:{app.name}]
use = egg:{app.name}
pyramid.reload_templates = false
pyramid.debug_authorization = false
pyramid.debug_notfound = false
pyramid.debug_routematch = false
pyramid.default_locale_name = en
pyramid.includes =
    pyramid_tm
    pyramid_exclog

sqlalchemy.url = {app.sqlalchemy_url}
exclog.extra_info = true
clld.environment = production
clld.files = {app.www}/files
clld.home = {app.home}
blog.host = {bloghost}
blog.user = {bloguser}
blog.password = {blogpassword}

%s

[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = {app.port}
workers = {app.workers}
proc_name = {app.name}

[loggers]
keys = root, {app.name}, sqlalchemy, exc_logger

[handlers]
keys = console, exc_handler

[formatters]
keys = generic, exc_formatter

[logger_root]
level = WARN
handlers = console

[logger_{app.name}]
level = WARN
handlers =
qualname = {app.name}

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_exc_logger]
level = ERROR
handlers = exc_handler
qualname = exc_logger

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[handler_exc_handler]
class = handlers.SMTPHandler
args = (('localhost', 25), '{app.name}@{env.host}', ['{config.ERROR_EMAIL}'], '{app.name} Exception')
level = ERROR
formatter = exc_formatter

[formatter_generic]
format = %%(asctime)s %%(levelname)-5.5s [%%(name)s][%%(threadName)s] %%(message)s

[formatter_exc_formatter]
format = %%(asctime)s %%(message)s
"""

CONFIG_TEMPLATES = {
    'test': _CONFIG_TEMPLATE % """\
[filter:paste_prefix]
use = egg:PasteDeploy#prefix
prefix = /{app.name}

[pipeline:main]
pipeline =
    paste_prefix
    {app.name}
""",
    'production': _CONFIG_TEMPLATE % """\
[pipeline:main]
pipeline =
    {app.name}
""",
}


def hashpw(pw):
    letters = 'abcdefghijklmnopqrstuvwxyz' \
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
        '0123456789/.'
    return crypt.crypt(pw, random.choice(letters) + random.choice(letters))


def install_repos(name):
    sudo('pip install -e git+%s#egg=%s' % (config.repos(name), name))


def create_file_as_root(path, content, **kw):
    require.files.file(
        str(path), contents=content, owner='root', group='root', use_sudo=True, **kw)


def get_template_variables(app, monitor_mode=False, with_blog=False):
    if monitor_mode and not os.environ.get('NEWRELIC_API_KEY'):
        print('--> Warning: no newrelic api key found in environment')  # pragma: no cover

    res = dict(
        app=app,
        env=env,
        newrelic_api_key=os.environ.get('NEWRELIC_API_KEY'),
        config=config,
        gunicorn=app.bin('gunicorn_paster'),
        newrelic=app.bin('newrelic-admin'),
        monitor_mode=monitor_mode,
        auth='',
        bloghost='',
        bloguser='',
        blogpassword='')

    if with_blog:  # pragma: no cover
        for key, default in [
            ('bloghost', 'blog.%s' % app.domain), ('bloguser', app.name)
        ]:
            custom = raw_input('Blog %s [%s]: ' % (key[4:], default))
            res[key] = custom if custom else default

        res['blogpassword'] = getpass(prompt='Blog password: ')
        assert res['blogpassword']

    return res


@task
def supervisor(app, command, template_variables=None):
    """
    .. seealso: http://serverfault.com/a/479754
    """
    template_variables = template_variables or get_template_variables(app)
    assert command in SUPERVISOR_TEMPLATE
    create_file_as_root(
        app.supervisor,
        SUPERVISOR_TEMPLATE[command].format(**template_variables), mode='644')
    if command == 'run':
        sudo('supervisorctl reread')
        sudo('supervisorctl update %s' % app.name)
        sudo('supervisorctl restart %s' % app.name)
    else:
        sudo('supervisorctl stop %s' % app.name)
        #sudo('supervisorctl reread %s' % app.name)
        #sudo('supervisorctl update %s' % app.name)
    time.sleep(1)


def require_bibutils(app):  # pragma: no cover
    """
    tar -xzvf bibutils_5.0_src.tgz -C /home/{app.name}
    cd /home/{app.name}/bibutils_5.0
    configure
    make
    sudo make install
    """
    if not exists('/usr/local/bin/bib2xml'):
        tgz = app.venv.joinpath('src', 'clld', 'tools',  'bibutils_5.0_src.tgz')
        sudo('tar -xzvf {tgz} -C {app.home}'.format(tgz=tgz, app=app))
        with cd(app.home.joinpath('bibutils_5.0')):
            sudo('./configure')
            sudo('make')
            sudo('make install')


@task
def uninstall(app):  # pragma: no cover
    for file_ in [app.supervisor, app.nginx_location, app.nginx_site]:
        if exists(file_):
            sudo('rm %s' % file_)
    service.reload('nginx')
    sudo('supervisorctl stop %s' % app.name)


@task
def maintenance(app, hours=2, template_variables=None):
    """turn maintenance mode on|off
    """
    template_variables = template_variables or get_template_variables(app)
    ts = utc.localize(datetime.utcnow() + timedelta(hours=hours))
    ts = ts.astimezone(timezone('Europe/Berlin')).strftime('%Y-%m-%d %H:%M %Z%z')
    require.files.directory(app.www, use_sudo=True)
    create_file_as_root(
        app.www.joinpath('503.html'),
        HTTP_503_TEMPLATE.format(timestamp=ts, **template_variables))


def http_auth(app):
    pwds = {
        app.name: getpass(prompt='HTTP Basic Auth password for user %s: ' % app.name),
        'admin': ''}

    while not pwds['admin']:
        pwds['admin'] = getpass(prompt='HTTP Basic Auth password for user admin: ')

    create_file_as_root(
        app.nginx_htpasswd,
        ''.join('%s:%s\n' % (name, hashpw(pw)) for name, pw in pwds.items()))

    return bool(pwds[app.name]), """\
        proxy_set_header Authorization $http_authorization;
        proxy_pass_header  Authorization;
        auth_basic "%s";
        auth_basic_user_file %s;""" % (app.name, app.nginx_htpasswd)


@task
def copy_files(app):
    data_dir = data_file(import_module(app.name))
    tarball = '/tmp/%s-files.tgz' % app.name
    local('tar -C %s -czf %s files' % (data_dir, tarball))
    require.files.file(tarball, source=tarball)
    if os.path.exists(tarball):
        os.remove(tarball)  # pragma: no cover
    with cd('/tmp'):
        tarfile = tarball.split('/')[2]
        sudo('tar -xzf %s' % tarfile)
        target = app.www.joinpath('files')
        if exists(target):
            sudo('cp -ru files/* %s' % target)
            sudo('rm -rf files')
        else:
            sudo('mv files %s' % app.www)  # pragma: no cover
        sudo('chown -R root:root %s' % target)
        sudo('rm %s' % tarfile)
        sudo('tree %s' % app.www)


@task
def deploy(app, environment, with_alembic=False, with_blog=False):
    template_variables = get_template_variables(
        app,
        monitor_mode='true' if environment == 'production' else 'false',
        with_blog=with_blog)

    require.users.user(app.name, shell='/bin/bash')
    require.postfix.server(env['host'])
    require.postgres.server()
    for pkg in [
        'libpq-dev',
        'git',
        'nginx',
        'supervisor',
        'openjdk-6-jre',
        'make',
        'sqlite3',
        'curl',
    ]:
        require.deb.package(pkg)
    require.postgres.user(app.name, app.name)
    require.postgres.database(app.name, app.name)
    require.files.directory(app.venv, use_sudo=True)
    require.python.virtualenv(app.venv, use_sudo=True)
    require.files.directory(app.logs, use_sudo=True)

    with virtualenv(app.venv):
        sudo('pip install -U pip')
        require.python.package('gunicorn', use_sudo=True)
        for repos in ['clld'] + getattr(app, 'dependencies', []) + [app.name]:
            install_repos(repos)
        sudo('webassets -m %s.assets build' % app.name)

    require_bibutils(app)

    #
    # configure nginx:
    #
    require.files.directory(
        str(app.nginx_location.dirname()), owner='root', group='root', use_sudo=True)

    restricted, auth = http_auth(app)
    if restricted:
        template_variables['auth'] = auth
    template_variables['admin_auth'] = auth

    if environment == 'test':
        create_file_as_root('/etc/nginx/sites-available/default', DEFAULT_SITE)
        create_file_as_root(
            app.nginx_location, LOCATION_TEMPLATE.format(**template_variables))
    elif environment == 'production':
        create_file_as_root(app.nginx_site, SITE_TEMPLATE.format(**template_variables))
        create_file_as_root(
            '/etc/logrotate.d/{0}'.format(app.name),
            LOGROTATE_TEMPLATE.format(**template_variables))

    maintenance(app, hours=app.deploy_duration, template_variables=template_variables)
    service.reload('nginx')

    #
    # TODO: replace with initialization of db from data repos!
    #
    if confirm('Copy files?', default=False):
        execute(copy_files, app)

    if not with_alembic and confirm('Recreate database?', default=False):
        supervisor(app, 'pause', template_variables)
        local('pg_dump -f /tmp/{0.name}.sql {0.name}'.format(app))
        local('gzip -f /tmp/{0.name}.sql'.format(app))
        require.files.file(
            '/tmp/{0.name}.sql.gz'.format(app),
            source="/tmp/{0.name}.sql.gz".format(app))
        sudo('gunzip -f /tmp/{0.name}.sql.gz'.format(app))

        if postgres.database_exists(app.name):
            with cd('/var/lib/postgresql'):
                sudo('sudo -u postgres dropdb %s' % app.name)

            require.postgres.database(app.name, app.name)

        sudo('sudo -u {0.name} psql -f /tmp/{0.name}.sql -d {0.name}'.format(app))
    else:
        if exists(app.src.joinpath('alembic.ini')):
            if confirm('Upgrade database?', default=False):
                supervisor(app, 'pause', template_variables)
                with virtualenv(app.venv):
                    with cd(app.src):
                        sudo('sudo -u {0.name} {1} -n production upgrade head'.format(
                            app, app.bin('alembic')))

    create_file_as_root(
        app.config, CONFIG_TEMPLATES[environment].format(**template_variables))
    create_file_as_root(
        app.newrelic_config, NEWRELIC_TEMPLATE.format(**template_variables))

    supervisor(app, 'run', template_variables)

    time.sleep(5)
    res = run('curl http://localhost:%s/_ping' % app.port)
    assert json.loads(res)['status'] == 'ok'


@task
def run_script(app, script_name, *args):  # pragma: no cover
    with cd(app.home):
        sudo(
            '%s %s %s#%s %s' % (
                app.bin('python'),
                app.src.joinpath(app.name, 'scripts', '%s.py' % script_name),
                app.config.basename(),
                app.name,
                ' '.join('%s' % arg for arg in args),
            ),
            user=app.name)


@task
def create_downloads(app):  # pragma: no cover
    dl_dir = app.src.joinpath(app.name, 'static', 'download')
    require.files.directory(dl_dir, use_sudo=True, mode="777")
    # run the script to create the exports from the database as glottolog3 user
    run_script(app, 'create_downloads')
    require.files.directory(dl_dir, use_sudo=True, mode="755")


def bootstrap():  # pragma: no cover
    for pkg in 'vim tree nginx'.split():
        require.deb.package(pkg)

    sudo('/etc/init.d/nginx start')

    for cmd in [
        'wget -O /etc/apt/sources.list.d/newrelic.list http://download.newrelic.com/debian/newrelic.list',
        'apt-key adv --keyserver hkp://subkeys.pgp.net --recv-keys 548C16BF',
        'apt-get update',
        'apt-get install newrelic-sysmond',
        'nrsysmond-config --set license_key=%s' % os.environ['NEWRELIC_API_KEY'],
        '/etc/init.d/newrelic-sysmond start',
    ]:
        sudo(cmd)
