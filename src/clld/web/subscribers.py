from __future__ import unicode_literals, print_function, division, absolute_import

from pyramid.i18n import get_localizer, TranslationStringFactory

from clld.web.util import helpers
from clld.web.assets import environment


def add_renderer_globals(module, event):
    if event['request']:
        _add_localizer(event['request'])
        event['_'] = event['request'].translate
        prod = event['request'].registry.settings.get('clld.environment') == 'production'
        environment.debug = not prod
    else:
        event['_'] = lambda s, **kw: s
    event['assets'] = environment
    event['h'] = helpers
    event['u'] = module  # pragma: no cover
    if module:
        # this is the hook for clld apps to provide additional template context for
        # templates associated with default views: provide a python with an appropriately
        # named function, and this function will be invoked, passing the current template
        # context as keyword parameters, and adding the items from the returned dict
        # to the template context.
        _renderer = event.get('renderer_name', '')
        if _renderer.endswith('.mako'):
            func = getattr(module, _renderer[:-5].replace('/', '_').replace('.', '_'), 0)
            if func:
                for k, v in func(**event).items():
                    event[k] = v


tsf = TranslationStringFactory('clld')


def add_localizer(event):
    _add_localizer(event.request)


def _add_localizer(request):
    if hasattr(request, 'translate'):
        return

    request._LOCALE_ = 'en'
    localizer = get_localizer(request)

    def auto_translate(*args, **kwargs):
        return localizer.translate(tsf(*args, **kwargs))

    request.translate = auto_translate


def init_map(event):
    event.request.map = event.request.get_map()
