"""
deploy with varnish:

- apt-get install varnish
- create /etc/default/varnish
- create /etc/varnish/main.vcl
- create /etc/varnish/sites.vcl
- create /etc/varnish/sites/
  (and require it to contain the correct include!)
- create /etc/varnish/sites/{app.name}.vcl
- /etc/init.d/varnish restart
- adapt nginx site config
- /etc/init.d/nginx reload
"""
from path import path
from fabric.contrib.files import append, exists
from fabtools import require
from fabtools import service

from clld.deploy.util import (
    create_file_as_root, SITE_TEMPLATE, get_template_variables, http_auth,
)
from clld.deploy.config import App


DEFAULT = """
START=yes
NFILES=131072
MEMLOCK=82000
# Default varnish instance name is the local nodename.  Can be overridden with
# the -n switch, to have more instances on a single server.
# INSTANCE=$(uname -n)
DAEMON_OPTS="-a :6081 \
             -T localhost:6082 \
             -t 3600 \
             -f /etc/varnish/main.vcl \
             -S /etc/varnish/secret \
             -s file,/var/lib/varnish/$INSTANCE/varnish_storage.bin,10G"
"""

MAIN_VCL = """
sub vcl_recv {
    set req.http.Host = regsub(req.http.Host, "^www\.", "");
    set req.http.Host = regsub(req.http.Host, ":80$", "");
}

include "/etc/varnish/sites.vcl";
"""

SITE_VCL_TEMPLATE = """
backend {app.name} {{
    .host = "127.0.0.1";
    .port = "{app.port}";
}}

sub vcl_recv
{{
    if (req.http.host ~ "^{app.domain}$")  {{ set req.backend = {app.name}; }}
}}

sub vcl_fetch {{
    set beresp.ttl = 3600s;
    return(deliver);
}}
"""


def cache(app):
    """require an app to be put behind varnish
    """
    require.deb.package('varnish')
    create_file_as_root('/etc/default/varnish', DEFAULT)
    create_file_as_root('/etc/varnish/main.vcl', MAIN_VCL)

    sites_vcl = '/etc/varnish/sites.vcl'
    site_config = path('/etc/varnish/sites/{app.name}.vcl'.format(app=app))
    include = 'include "%s";' % site_config
    if exists(sites_vcl):
        append(sites_vcl, include, use_sudo=True)
    else:
        create_file_as_root(sites_vcl, include + '\n')

    require.files.directory(str(site_config.dirname()), use_sudo=True)
    create_file_as_root(site_config, SITE_VCL_TEMPLATE.format(app=app))
    service.restart('varnish')

    create_file_as_root(
        app.nginx_site,
        SITE_TEMPLATE.format(**get_template_variables(App(app.name, 6081, domain=app.domain))))
    service.reload('nginx')


def uncache(app):
    tv = get_template_variables(app)
    tv['auth'] = http_auth(app)
    create_file_as_root(app.nginx_site, SITE_TEMPLATE.format(**tv))
    service.reload('nginx')
