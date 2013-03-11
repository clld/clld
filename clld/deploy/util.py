"""
Deployment utilities for clld apps
"""
#
# TODO: logrotate!
#
import time
import json
import crypt
import random
from getpass import getpass

try:
    from fabric.api import sudo, run, local, put, env, cd
    from fabric.contrib.console import confirm
    from fabtools import require
    from fabtools.python import virtualenv
    from fabtools import service
    from fabtools import postgres
except ImportError:  # pragma: no cover
    sudo, run, local, put, env, cd, confirm, require, virtualenv, service, postgres = \
    None, None, None, None, None, None, None, None, None, None, None

from clld.deploy import config


DEFAULT_SITE = """\
server {
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

location /{app.name}/clld-static/ {{
        alias {app.venv}/src/clld/clld/web/static/;
}}

location /{app.name}/static/ {{
        alias {app.venv}/src/{app.name}/{app.name}/static/;
}}
"""

SITE_TEMPLATE = """\
server {{
    server_name {app.host};
    access_log /var/logs/{app.name}/access.log main;

    root {app.www};

    location / {{
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Forwarded-For  $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_connect_timeout 10;
            proxy_read_timeout 10;
            proxy_pass http://127.0.0.1:{app.port}/;
    }}

    location /clld-static/ {{
            alias {app.venv}/src/clld/clld/web/static/;
    }}

    location /static/ {{
            alias {app.venv}/src/{app.name}/{app.name}/static/;
    }}
}}
"""

_SUPERVISOR_TEMPLATE = """\
[program:{app.name}]
command={gunicorn} -u {app.name} -g {app.name} --error-logfile {app.error_log} {app.config}
autostart=%s
autorestart=%s
redirect_stderr=True
"""
SUPERVISOR_TEMPLATE = {
    'pause': _SUPERVISOR_TEMPLATE % ('false', 'false'),
    'run': _SUPERVISOR_TEMPLATE % ('true', 'true'),
}

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

%s

[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = {app.port}
workers = 3
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


def supervisor(app, command, template_variables):
    assert command in SUPERVISOR_TEMPLATE
    sudo('/etc/init.d/supervisor stop')
    create_file_as_root(
        app.supervisor,
        SUPERVISOR_TEMPLATE[command].format(**template_variables), mode='644')
    sudo('/etc/init.d/supervisor start')


def deploy(app, environment):
    template_variables = dict(
        app=app,
        env=env,
        config=config,
        gunicorn=app.bin('gunicorn_paster'),
        auth='')

    require.users.user(app.name, shell='/bin/bash')
    require.postfix.server(env['host'])
    require.postgres.server()
    for pkg in ['libpq-dev', 'git', 'nginx', 'supervisor']:
        require.deb.package(pkg)
    require.postgres.user(app.name, app.name)
    require.postgres.database(app.name, app.name)
    require.files.directory(app.venv, use_sudo=True)
    require.python.virtualenv(app.venv, use_sudo=True)
    require.files.directory(app.logs, use_sudo=True)

    with virtualenv(app.venv):
        require.python.package('gunicorn', use_sudo=True)
        install_repos('clld')
        install_repos(app.name)

    #
    # TODO: replace with initialization of db from data repos!
    #
    if confirm('Recreate database?', default=False):
        local('pg_dump -f /tmp/{0.name}.sql {0.name}'.format(app))
        require.files.file('/tmp/{0.name}.sql'.format(app), source="/tmp/{0.name}.sql".format(app))

        if postgres.database_exists(app.name):
            supervisor(app, 'pause', template_variables)

            with cd('/var/lib/postgresql'):
                sudo('sudo -u postgres dropdb %s' % app.name)

            require.postgres.database(app.name, app.name)

        sudo('sudo -u {0.name} psql -f /tmp/{0.name}.sql -d {0.name}'.format(app))

    create_file_as_root(
        app.config, CONFIG_TEMPLATES[environment].format(**template_variables))

    supervisor(app, 'run', template_variables)

    time.sleep(2)
    res = run('curl http://localhost:%s/_ping' % app.port)
    assert json.loads(res)['status'] == 'ok'

    if environment == 'test':
        create_file_as_root('/etc/nginx/sites-available/default', DEFAULT_SITE)
        require.files.directory(
            str(app.nginx_location.dirname()), owner='root', group='root', use_sudo=True)

        pw = getpass(prompt='HTTP Basic Auth password for user %s: ' % app.name)
        if pw:
            create_file_as_root(app.nginx_htpasswd, '%s:%s\n' % (app.name, hashpw(pw)))
            template_variables['auth'] = """\
        auth_basic "%s";
        auth_basic_user_file %s;""" % (app.name, app.nginx_htpasswd)

        create_file_as_root(
            app.nginx_location, LOCATION_TEMPLATE.format(**template_variables))
    elif environment == 'production':
        create_file_as_root(app.nginx_site, SITE_TEMPLATE.format(**template_variables))

    service.reload('nginx')
