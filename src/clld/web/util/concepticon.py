from clld.web.util.htmllib import HTML
from clld.web.util.helpers import external_link

__all__ = ['BASE_URL', 'url', 'logo', 'link']

BASE_URL = 'https://concepticon.clld.org'


def url(id=None, obj_type='ConceptSet'):
    if id is None:
        return BASE_URL
    path_map = {
        'ConceptSet': 'parameters',
        'ConceptList': 'contributions',
        'Concept': 'values',
    }
    return '{0}/{1}/{2}'.format(BASE_URL, path_map[obj_type], id)


def logo(req, width='20'):
    return HTML.img(src=req.static_url('clld:web/static/images/concepticon.png'), width=width)


def link(req, id=None, obj_type='ConceptSet', label=None):
    akw = dict(
        title='Concepticon' if id is None else 'View {0} at Concepticon'.format(obj_type),
        href=url(id=id, obj_type=obj_type))
    if label:
        return external_link(None, label=label, **akw)
    return HTML.a(logo(req), **akw)
