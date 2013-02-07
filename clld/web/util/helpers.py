from json import dumps
from itertools import groupby

from clld import interfaces
from clld import RESOURCES
from clld.web.util.htmllib import HTML
from clld.db.meta import DBSession
from clld.db.models import common as models


class JS(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, *args):
        return '%s(%s)' % (self.name, ', '.join(
            arg.name if isinstance(arg, JS) else dumps(arg) for arg in args))

    def __getattr__(self, attr):
        return JS('%s.%s' % (self.name, attr))


JSMap = JS('CLLD.Map')
JSModal = JS('CLLD.Modal')
JSDataTable = JS('CLLD.DataTable')


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
    if not label and rsc.interface == interfaces.IValue and obj.domainelement:
        label = obj.domainelement.name
    #if rsc.interface == interfaces.IValue:
    #    label = '%s, %s, %s' % (obj.language.name, obj.parameter.name, label)
    #if rsc.interface == interfaces.ISentence:
    #    label = '%s, %s' % (obj.language.name, label)
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
