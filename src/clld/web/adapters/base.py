"""Base classes for adapters."""
from __future__ import unicode_literals
from uuid import uuid4

from zope.interface import implementer
from pyramid.response import Response
from pyramid.renderers import render as pyramid_render
from six import text_type
from clldutils.misc import slug

from clld import interfaces


class Renderable(object):

    """Virtual base class for adapters.

    Adapters can provide custom behaviour either by specifying a template to use for
    rendering, or by overwriting the render method.
    """

    name = None
    template = None
    mimetype = 'text/plain'
    extension = None
    send_mimetype = None
    rel = 'alternate'
    content_type_params = None

    def __init__(self, obj):
        self.obj = obj

    @property
    def label(self):
        return getattr(self, '__label__', self.__class__.__name__)

    @property
    def charset(self):
        return 'utf-8' \
            if self.mimetype.startswith('text/') \
            or 'xml' in self.mimetype \
            or 'kml' in self.mimetype \
            else None

    def render_to_response(self, ctx, req):
        res = Response(self.render(ctx, req))
        res.vary = str('Accept')
        res.content_type = str(self.send_mimetype or self.mimetype)
        if self.charset:
            res.content_type += str('; charset=') + str(self.charset)
        if self.content_type_params:
            d = res.content_type_params
            for k, v in self.content_type_params.items():
                d[str(k)] = str(v)
            res.content_type_params = d
        return res

    def template_context(self, ctx, req):
        return {}

    def render(self, ctx, req):
        context = self.template_context(ctx, req)
        context.setdefault('ctx', ctx)
        return pyramid_render(self.template, context, request=req)


@implementer(interfaces.IRepresentation)
class Representation(Renderable):

    """Base class for adapters implementing IRepresentation."""


class _Json(Renderable):

    """JavaScript Object Notation."""

    name = 'JSON'
    mimetype = 'application/json'
    extension = 'json'

    def render(self, ctx, req):
        return pyramid_render('json', ctx, request=req)


@implementer(interfaces.IRepresentation)
class Json(_Json):
    pass


@implementer(interfaces.IIndex)
class JsonIndex(_Json):
    pass


@implementer(interfaces.IIndex)
class Index(Renderable):

    """Base class for adapters implementing IIndex."""


def adapter_factory(*args, **kw):
    # for backwards compatibility we interpret the first positional argument as template:
    if args:
        kw['template'] = args[0]
    assert 'template' in kw
    kw.setdefault('mimetype', 'text/html')
    kw.setdefault('extension', 'html')
    base = kw.pop('base', Representation)
    return type(str('AdapterFromFactory%s' % slug(text_type(uuid4()))), (base,), kw)
