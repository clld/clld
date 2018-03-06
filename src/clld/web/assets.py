from __future__ import unicode_literals, print_function, division, absolute_import

from webassets import Environment, Bundle
from clldutils.path import Path

import clld


def skip(_in, out, **kw):
    """filter to skip content of assets which are fetched from CDN in production."""
    out.write('')  # pragma: no cover


_static_path = Path(clld.__file__).parent.joinpath('web', 'static').as_posix()
environment = Environment(
    _static_path, '/clld:web/static/', manifest='json:', auto_build=False)
environment.append_path(_static_path, url='/clld:web/static/')

bundles = {
    'js': [
        Bundle(
            'js/jquery.js',
            'js/leaflet-src.js',
            'js/Leaflet.fullscreen.js',
            filters=(skip,)),
        'js/bootstrap.min.js',
        'js/jquery.dataTables.min.js',
        'js/oms.min.js',
        Bundle(
            'js/bootstrapx-clickover.js',
            'js/tree.jquery.js',
            'js/leaflet-providers.js',
            'js/leaflet-hash.js',
            'js/clld.js',
            'project.js',
            filters='yui_js'),
    ],
    'css': [
        Bundle(
            'css/leaflet.css',
            'css/leaflet.fullscreen.css',
            filters=(skip,)),
        Bundle(
            'css/clld.css',
            'css/jqtree.css',
            'css/hint.css',
            'css/jquery.dataTables.css',
            filters='yui_css'),
        'css/bootstrap.min.css',
        'css/bootstrap-responsive.min.css',
        Bundle(
            'project.css',
            filters='yui_css'),
    ],
}

for name in bundles:
    environment.register(
        name, *bundles[name], **dict(output='{0}/packed.%(version)s.{0}'.format(name)))
