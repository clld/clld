from pyramid.i18n import get_localizer, TranslationStringFactory

from clld.web.util import helpers


def add_renderer_globals(event):
    event['_'] = event['request'].translate
    event['h'] = helpers


tsf = TranslationStringFactory('clld')

def add_localizer(event):
    event.request._LOCALE_ = 'en'
    localizer = get_localizer(event.request)
    def auto_translate(*args, **kwargs):
        return localizer.translate(tsf(*args, **kwargs))
    event.request.translate = auto_translate
