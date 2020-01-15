"""
view callables implementing the sitemap protocol.

.. seealso:: http://www.sitemaps.org/
"""
import operator
import itertools

from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy import join, and_, true

from clld import RESOURCES
from clld.db.meta import DBSession
from clld.db.models import common
from clld.web.util.helpers import get_url_template


# http://www.sitemaps.org/protocol.html#index
LIMIT = 50000


def robots(req):
    """robots.txt response listing the sitemaps.

    .. seealso:: http://www.sitemaps.org/protocol.html#submit_robots
    """
    return Response(
        "Sitemap: %s\n" % req.route_url('sitemapindex'), content_type="text/plain")


def _query(req, rsc):
    """Ordered sqlalchemy query.

    We must make sure, each query is ordered, so that limit and offset does make sense.
    """
    return DBSession.query(rsc.model.id, rsc.model.updated).order_by(rsc.model.pk)


def _e(name, *content):
    return '<{0}>{1}</{0}>'.format(name, ''.join(content))


def _response(type_, itemiter):
    def serialize(item):
        name = 'url' if type_ == 'urlset' else 'sitemap'
        return _e(name, *[_e(k, v) for k, v in item.items()])

    return Response(
        """\
<?xml version="1.0" encoding="UTF-8"?>
<{0} xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{1}
</{0}>""".format(type_, '\n'.join(map(serialize, itemiter))),
        content_type="application/xml")


def sitemapindex(req):
    """Response listing resource-specific sitemaps.

    .. seealso:: http://www.sitemaps.org/protocol.html#index
    """
    def _iter(sitemaps):
        for r in RESOURCES:
            if r.with_index and r.name in sitemaps:
                n, m = divmod(_query(req, r).count(), LIMIT)
                if m:
                    n += 1
                for i in range(n):
                    yield dict(loc=req.route_url('sitemap', rsc=r.name, n=i))

    return _response(
        'sitemapindex', _iter(req.registry.settings.get('clld.sitemaps', [])))


def sitemap(req):
    """Resource-specific sitemap.

    .. note:: The resource is looked up using the URL parameter ``rsc``.

    .. seealso:: http://www.sitemaps.org/protocol.html#xmlTagDefinitions
    """
    def _iter():
        for r in RESOURCES:
            if r.name == req.matchdict['rsc']:
                query = _query(req, r)\
                    .offset(LIMIT * int(req.matchdict['n']))\
                    .limit(LIMIT)
                for id_, updated in query:
                    yield dict(
                        loc=req.route_url(r.name, id=id_),
                        lastmod=str(updated).split(' ')[0])
    return _response('urlset', _iter())


def resourcemap(req):
    """Resource-specific JSON response listing all resource instances."""
    rsc = req.params.get('rsc')
    if rsc == 'language':
        q = DBSession.query(
            common.Language.id,
            common.Language.name,
            common.Language.latitude,
            common.Language.longitude,
            common.Identifier.type.label('itype'),
            common.Identifier.name.label('iname')
        ).select_from(common.Language).outerjoin(join(
            common.LanguageIdentifier,
            common.Identifier, and_(
                common.LanguageIdentifier.identifier_pk == common.Identifier.pk,
                common.Identifier.type != 'name')
        )).filter(common.Language.active == true()).order_by(common.Language.id)

        def resources():
            for (id, name, lat, lon), rows in itertools.groupby(q, operator.itemgetter(0, 1, 2, 3)):
                identifiers = [
                    {'type': r.itype, 'identifier': r.iname.lower()
                     if r.itype.startswith('WALS') else r.iname}
                    for r in rows if r.iname is not None]
                yield {'id': id, 'name': name, 'latitude': lat, 'longitude': lon,
                       'identifiers': identifiers}
    elif rsc == 'parameter':
        q = DBSession.query(
            common.Parameter.id,
            common.Parameter.name
        ).order_by(common.Parameter.pk)

        def resources():
            for id, name in q:
                yield {'id': id, 'name': name}
    else:
        return HTTPNotFound()

    return {
        'properties': {
            'dataset': req.dataset.id,
            'uri_template': get_url_template(req, rsc, relative=False)},
        'resources': list(resources())}
