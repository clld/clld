from webassets import Environment, Bundle
from path import path

import clld


environment = Environment(
    path(clld.__file__).dirname().joinpath('web', 'static'), '/clld-static')

environment.register(
    'js',
    # Note: in production jquery is loaded from CDN
    'js/bootstrap.min.js',
    'js/jquery.dataTables.min.js',
    Bundle('js/bootstrapx-clickover.js', 'js/tree.jquery.js', 'js/clld.js', filters='yui_js'),
    output='js/packed.js')

environment.register(
    'css',
    Bundle('css/clld.css', 'css/jqtree.css', filters='yui_css'),
    'css/bootstrap.min.css',
    'css/bootstrap-responsive.min.css',
    output='css/packed.css')
