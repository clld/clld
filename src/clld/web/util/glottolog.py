from clld.web.util.htmllib import HTML

__all__ = ['BASE_URL', 'url', 'logo', 'link']

BASE_URL = 'https://glottolog.org'


def url(id=None, obj_type='languoid'):
    if id is None:
        return BASE_URL
    assert obj_type in ('languoid', 'reference')
    return '{0}/resource/{1}/id/{2}'.format(BASE_URL, obj_type, id)


def logo(req, width='20'):
    return HTML.img(
        src=req.static_url('clld:web/static/images/glottolog.png'),
        width=width,
        style="margin-top: -2px")


def link(req, id=None, obj_type='languoid', label=None):
    akw = dict(
        title='Glottolog' if id is None else 'View {0} at Glottolog'.format(obj_type),
        href=url(id=id, obj_type=obj_type))
    return HTML.a(logo(req), label or '', **akw)
