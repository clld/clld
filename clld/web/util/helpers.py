from json import dumps

from clld import RESOURCES
from clld.web.util.htmllib import HTML


def link(req, obj, **kw):
    rsc = None
    for _rsc in RESOURCES:
        if _rsc.interface.providedBy(obj):
            rsc = _rsc
            break

    assert rsc
    href = kw.pop('href', req.route_url(rsc.name, id=obj.id))
    label = kw.pop('label', getattr(obj, 'name', obj.id))
    kw.setdefault('title', label)
    return HTML.a(label, href=href, **kw)


def external_link(url, label=None):
    return HTML.a(icon('share'), ' ', label or url, href=url)


def button(*content, **attrs):
    attrs.setdefault('type', 'button')
    class_ = attrs['class'] if 'class' in attrs else attrs.pop('class_', '').split()
    if 'btn' not in class_:
        class_.append('btn')
    attrs['class'] = ' '.join(class_)
    return HTML.button(*content, **attrs)


def icon(class_, inverted=False):
    if not class_.startswith('icon-'):
        class_ = 'icon-' + class_
    if inverted:
        class_ = '%s icon-white' % class_
    return HTML.i(class_=class_)


def text2html(text):
    chunks = []
    for i, line in enumerate(text.split('\n')):
        if i > 0:
            chunks.append(HTML.br())
        chunks.append(line)
    return HTML.p(*chunks)
