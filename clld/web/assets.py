from webassets import Environment, Bundle
from path import path

import clld


def skip(_in, out, **kw):
    """filter to skip content of assets which are fetched from CDN in production.
    """
    out.write('')  # pragma: no cover

environment = Environment(
    path(clld.__file__).dirname().joinpath('web', 'static'),
    '/clld:web/static/',
    manifest='json:',
    auto_build=False)

environment.append_path(
    path(clld.__file__).dirname().joinpath('web', 'static'), url='/clld:web/static/')

bundles = {
    'js': [
        Bundle(
            'js/jquery-1.8.2.js',
            'js/leaflet-src.js',
            filters=(skip,)),
        'js/bootstrap.min.js',
        'js/jquery.dataTables.min.js',
        'js/oms.min.js',
        Bundle(
            'js/bootstrapx-clickover.js',
            'js/tree.jquery.js',
            'js/leaflet-providers.js',
            'js/leaflet.label.js',
            'js/Control.FullScreen.js',
            'js/leaflet-hash.js',
            'js/clld.js',
            'project.js',
            filters='yui_js'),
    ],
    'css': [
        Bundle(
            'css/clld.css',
            'css/jqtree.css',
            'css/leaflet.css',
            'css/leaflet.label.css',
            'css/hint.css',
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
