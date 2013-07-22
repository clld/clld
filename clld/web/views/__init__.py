from json import dumps
import re

from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPNotAcceptable, HTTPFound, HTTPNotFound, HTTPMultipleChoices,
)
from pyramid.interfaces import IRoutesMapper
from pyramid.renderers import render

from clld.interfaces import IRepresentation, IIndex, IMetadata
from clld import RESOURCES
from clld.web.adapters import get_adapter, get_adapters
from clld.db.models.common import Language


def view(interface, ctx, req):
    """renders a resource as pyramid response using the most appropriate adapter
    for the accept header sent.
    """
    adapter = get_adapter(
        interface, ctx, req, ext=req.matchdict and req.matchdict.get('ext'))
    if not adapter:
        raise HTTPNotAcceptable()
    return adapter.render_to_response(ctx, req)


def index_view(ctx, req):
    if req.is_xhr and 'sEcho' in req.params:
        return datatable_xhr_view(ctx, req)
    return view(IIndex, ctx, req)


def resource_view(ctx, req):
    return view(IRepresentation, ctx, req)


def datatable_xhr_view(ctx, req):
    # call get_query, thereby - as side effect - making sure, the counts are set.
    items = ctx.get_query()
    if hasattr(ctx, 'row_class'):
        data = []
        for item in items:
            _d = {'DT_RowId': 'row_%s' % item.pk}
            row_class = ctx.row_class(item)
            if row_class:
                _d['DT_RowClass'] = row_class
            for i, col in enumerate(ctx.cols):
                _d[str(i)] = col.format(item)
            data.append(_d)
    else:
        data = [[col.format(item) for col in ctx.cols] for item in items]

    # sEcho parameter.
    # Note that it strongly recommended for security reasons that you 'cast' this
    # parameter to an integer in order to prevent Cross Site Scripting (XSS) attacks.
    try:
        echo = int(req.params['sEcho'])
    except ValueError:
        echo = 1

    res = {
        "aaData": data,
        "sEcho": str(echo),
        "iTotalRecords": ctx.count_all,
        "iTotalDisplayRecords": ctx.count_filtered,
    }
    return Response(dumps(res), content_type='application/json')


def js(req):
    param_pattern = re.compile('\{(?P<name>[a-z]+)(\:[^\}]+)?\}')

    res = ["CLLD.base_url = %s;" % dumps(req.application_url)]
    for route in req.registry.getUtility(IRoutesMapper).get_routes():
        pattern = param_pattern.sub(lambda m: '{%s}' % m.group('name'), route.pattern)
        res.append('CLLD.routes[%s] = %s;' % tuple(map(dumps, [route.name, pattern])))
    return Response('\n'.join(res), content_type="text/javascript")


def _raise(req):
    raise ValueError('test')


def _ping(req):
    return {'status': 'ok'}


def unapi(req):
    """implements the server side of the unAPI spec.
    """
    id_ = req.params.get('id')
    if id_:
        obj = req.ctx_for_url(id_)
        if not obj:
            return HTTPNotFound()

    format_ = req.params.get('format')
    if not format_:
        kw = {'content_type': 'application/xml'}
        if id_:
            formats = [a for n, a in get_adapters(IMetadata, obj, req)]
            kw['status'] = '300 Multiple Choices'
        else:
            formats = []
        body = render(
            'unapiformats.mako',
            {'formats': formats, 'identifier': id_},
            request=req)
        return Response(body, **kw)

    if not id_:
        return HTTPNotFound()

    adapter = None
    for _n, _a in get_adapters(IMetadata, obj, req):
        if _a.unapi_name == format_:
            adapter = _a
            break
    if not adapter:
        return HTTPNotAcceptable()
    return HTTPFound(location=req.resource_url(obj, ext=adapter.extension))
