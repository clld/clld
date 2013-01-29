from json import dumps

from clld import interfaces
from clld import RESOURCES
from clld.web.util.htmllib import HTML


def link(req, obj, **kw):
    rsc = None
    for _rsc in RESOURCES:
        if _rsc.interface.providedBy(obj):
            rsc = _rsc
            break

    assert rsc
    kw.setdefault('class', rsc.interface.__name__[1:])
    href = kw.pop('href', req.resource_url(obj, rsc=rsc, **kw.pop('url_kw', {})))
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


def linked_contributors(req, contribution):
    chunks = []
    for i, c in enumerate(contribution.primary_contributors):
        if i > 0:
            chunks.append(' and ')
        chunks.append(link(req, c))

    for i, c in enumerate(contribution.secondary_contributors):
        if i == 0:
            chunks.append(' with ')
        if i > 0:
            chunks.append(' and ')
        chunks.append(link(req, c))

    return HTML.span(*chunks)
