"""View logic for clld default views."""
import re
import json
import functools

from pyramid.response import Response
import pyramid.httpexceptions
from pyramid.interfaces import IRoutesMapper
from pyramid.renderers import render, render_to_response

from clld.interfaces import IRepresentation, IIndex, IMetadata
from clld.web.adapters import get_adapter, get_adapters
from clld.web.adapters.csv import CsvAdapter, CsvmJsonAdapter
from clld.web.util.multiselect import MultiSelect
from clld.db.models.common import Combination
from clld.web.maps import CombinedMap


def xpartial(func, *args, **kw):
    """Augment partial to make it possible to register partials as view callables.

    >>> f = xpartial(lambda x, y: x + y, 1)
    >>> assert f(1) == 2
    """
    res = functools.partial(func, *args, **kw)
    res.__module__ = func.__module__
    return res


def redirect(cls, location, ctx, req=None):
    """Can be used with xpartial to register views that simply redirect.

    >>> view = xpartial(pyramid.httpexceptions.HTTPFound, lambda req: req.route_url('.'))
    """
    # workaround for https://github.com/Pylons/pyramid/issues/1428
    req = req or ctx
    if callable(location):
        location = location(req)
    raise cls(location=location)


def gone(ctx, req):
    """view callable."""
    raise pyramid.httpexceptions.HTTPGone()


def view(interface, ctx, req, getadapters=False):
    """Render a resource as pyramid response.

    Using the most appropriate adapter for the accept header sent.

    :param getadapters: If True, the adapter used to render the response and the list of\
    all available adapters for the context are returned as well.
    """
    #
    # if req.matched_route.name.endswith('_alt') -> add rel="canonical" header
    # else: add rel="alternate" header
    #
    adapter, adapters = get_adapter(
        interface, ctx, req, ext=req.matchdict and req.matchdict.get('ext'), getall=True)
    if not adapter:
        raise pyramid.httpexceptions.HTTPNotAcceptable()
    res = adapter.render_to_response(ctx, req)
    if getadapters:
        return res, adapter, adapters
    return res  # pragma: no cover


def _add_link_header(response, url, adapter=None, rel="canonical", mimetype="text/html"):
    if adapter:
        rel = adapter.rel
        mimetype = adapter.send_mimetype or adapter.mimetype
    if mimetype and rel:
        response.headerlist.append(
            ('Link', '<%s>; rel="%s"; type="%s"' % tuple(map(str, [url, rel, mimetype]))))


def index_view(ctx, req):
    if req.is_xhr and 'sEcho' in req.params:
        return datatable_xhr_view(ctx, req)
    res, current, adapters = view(IIndex, ctx, req, getadapters=True)
    if req.matched_route:
        if req.matched_route.name.endswith('_alt'):
            # add the canonical link:
            _add_link_header(res, req.route_url(req.matched_route.name[:-4]))
            if current.mimetype == CsvAdapter.mimetype:
                # If serving csv add link header to make metadata discoverable. See
                # http://www.w3.org/TR/2015/CR-tabular-data-model-20150716/#link-header
                csvm = [a for a in adapters if a.extension == CsvmJsonAdapter.extension]
                if csvm:
                    a = csvm[0]
                    _add_link_header(
                        res,
                        req.route_url(req.matched_route.name, ext=a.extension),
                        adapter=a)
        else:
            for a in [_a for _a in adapters if _a.rel and _a.extension]:
                _add_link_header(
                    res,
                    req.route_url(req.matched_route.name + '_alt', ext=a.extension),
                    adapter=a)
    return res


def resource_view(ctx, req):
    res, _, adapters = view(IRepresentation, ctx, req, getadapters=True)
    if req.matched_route:
        if req.matched_route.name.endswith('_alt'):
            _add_link_header(res, req.resource_url(ctx))
        else:
            for a in adapters:
                if a.rel and a.extension:
                    _add_link_header(
                        res, req.resource_url(ctx, ext=a.extension), adapter=a)
    return res


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
    return render_to_response('json', res, request=req)


def js(req):
    param_pattern = re.compile(r'\{(?P<name>[a-z]+)(\:[^\}]+)?\}')

    res = [
        "CLLD.base_url = %s;" % json.dumps(req.application_url),
        "CLLD.query_params = %s;" % json.dumps(req.query_params),
    ]
    for route in req.registry.getUtility(IRoutesMapper).get_routes():
        pattern = param_pattern.sub(lambda m: '{%s}' % m.group('name'), route.pattern)
        res.append('CLLD.routes[%s] = %s;' % tuple(map(json.dumps, [route.name, pattern])))
    return Response('\n'.join(res), content_type="text/javascript")


def select_combination(ctx, req):
    if 'parameters' in req.params:
        ids = req.params.getall('parameters')
        if len(ids) > 1:
            id_ = Combination.delimiter.join(ids)
        else:
            id_ = Combination.delimiter.join(req.params['parameters'].split(','))
        raise pyramid.httpexceptions.HTTPFound(req.route_url('combination', id=id_))
    raise pyramid.httpexceptions.HTTPNotFound


def _raise(req):
    """view callable to test error reporting in running apps."""
    raise ValueError('test')


def _ping(req):
    """view to test aliveness of apps."""
    return {'status': 'ok'}


def unapi(req):
    """View callable implementing the server side of the unAPI spec."""
    id_ = req.params.get('id')
    if id_:
        obj = req.ctx_for_url(id_)
        if not obj:
            return pyramid.httpexceptions.HTTPNotFound()

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
        return pyramid.httpexceptions.HTTPNotFound()

    adapter = None
    for _n, _a in get_adapters(IMetadata, obj, req):
        if _a.unapi_name == format_:
            adapter = _a
            break
    if not adapter:
        return pyramid.httpexceptions.HTTPNotAcceptable()
    return pyramid.httpexceptions.HTTPFound(
        location=req.resource_url(obj, ext=adapter.extension))


#
# The following code implements a view to show a map with parameters from distinct
# datasets. It may be used by CrossGram at some point.
#
class ParameterMultiSelect(MultiSelect):  # pragma: no cover

    """Experimental."""

    def __init__(self, req, name, eid, collection=None, url=None, selected=None):
        MultiSelect.__init__(self, req, name, eid, url='x')
        self.data = []
        for app, rm in req.registry.settings.get('clld.parameters', {}).items():
            for param in rm['resources']:
                self.data.append({
                    'id': '%s-%s' % (app, param['id']),
                    'text': '%s %s: %s' % (app, param['id'], param['name'])})
        self._datadict = dict((d['id'], d) for d in self.data)

    def format_result(self, obj):
        return obj

    def get_urls(self):
        for i, param in enumerate(self.req.params.get('parameters', '').split(',')):
            if param in self._datadict:
                if self.selected is None:
                    self.selected = []
                self.selected.append(self._datadict[param])
                app, pid = param.split('-', 1)
                rm = self.req.registry.settings['clld.parameters'][app]
                yield (app, pid, rm['properties']['uri_template'].format(id=pid))

    def get_default_options(self):
        return {
            'placeholder': "Select parameter",
            'width': 'off',
            'class': 'span6',
            'multiple': True,
            'data': self.data}


def combined(ctx, req):  # pragma: no cover
    res = {'map': None, 'select': ParameterMultiSelect(req, 'parameters', 'parameters')}
    urls = list(res['select'].get_urls())
    if urls:
        res['map'] = CombinedMap(urls, req)
    return res
