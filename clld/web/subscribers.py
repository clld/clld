from collections import defaultdict

from six import PY3
from pyramid.i18n import get_localizer, TranslationStringFactory

from clld import interfaces
from clld.web.util import helpers

if PY3:  # pragma: no cover
    class Environment(dict):
        debug = False

    class Bundle(object):
        def urls(self):
            return []

    environment = Environment(js=Bundle(), css=Bundle())
else:
    from clld.web.assets import environment


def add_renderer_globals(event):
    if event['request']:
        event['_'] = event['request'].translate
        prod = event['request'].registry.settings.get('clld.environment') == 'production'
        environment.debug = not prod
    else:
        event['_'] = lambda s, **kw: s
    event['assets'] = environment
    event['h'] = helpers


tsf = TranslationStringFactory('clld')


def add_localizer(event):
    event.request._LOCALE_ = 'en'
    localizer = get_localizer(event.request)

    def auto_translate(*args, **kwargs):
        return localizer.translate(tsf(*args, **kwargs))

    event.request.translate = auto_translate


def init_map(event):
    req = event.request
    req.map = None
    if req.matched_route:
        map_ = req.registry.queryUtility(interfaces.IMap, name=req.matched_route.name)
        if map_:
            req.map = map_(event.request.context, event.request)
