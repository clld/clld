"""
views implementing the sitemap protocol

.. seealso:: http://www.sitemaps.org/
"""
from pyramid.response import Response

from clld import RESOURCES
from clld.db.meta import DBSession


# http://www.sitemaps.org/protocol.html#index
LIMIT = 50000


def robots(req):
    """
    .. seealso:: http://www.sitemaps.org/protocol.html#submit_robots
    """
    return Response(
        "Sitemap: %s\n" % req.route_url('sitemapindex'), content_type="text/plain")


def _query(req, rsc):
    """we must make sure, each query is ordered, so that limit and offset does make sense.
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
    """
    .. seealso:: http://www.sitemaps.org/protocol.html#index
    """
    def _iter():
        for r in RESOURCES:
            if r.with_index:
                n, m = divmod(_query(req, r).count(), LIMIT)
                if m:
                    n += 1
                for i in range(n):
                    yield dict(loc=req.route_url('sitemap', rsc=r.name, n=i))

    return _response('sitemapindex', _iter())


def sitemap(req):
    """
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
