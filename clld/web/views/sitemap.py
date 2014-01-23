"""
views implementing the sitemap protocol

.. seealso:: http://www.sitemaps.org/
"""
from itertools import groupby

from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound

from clld import RESOURCES
from clld.db.meta import DBSession
from clld.db.models import common
from clld.web.util.helpers import get_url_template


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
    def _iter(sitemaps):
        for r in RESOURCES:
            if r.with_index and r.name in sitemaps:
                n, m = divmod(_query(req, r).count(), LIMIT)
                if m:
                    n += 1
                for i in range(n):
                    yield dict(loc=req.route_url('sitemap', rsc=r.name, n=i))

    return _response('sitemapindex', _iter(req.registry.settings.get('sitemaps', [])))


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


def resourcemap(req):
    res = {'properties': {'dataset': req.dataset.id}, 'resources': []}
    rsc = req.params.get('rsc')
    if rsc:
        res['properties']['uri_template'] = get_url_template(req, rsc, relative=False)
        if rsc == 'language':
            q = DBSession.query(
                common.Language.id,
                common.Language.name,
                common.Language.latitude,
                common.Language.longitude,
                common.Identifier.type,
                common.Identifier.name)\
                .join(common.Language.languageidentifier)\
                .join(common.LanguageIdentifier.identifier)\
                .filter(common.Language.active == True)\
                .filter(common.Identifier.type != 'name')\
                .order_by(common.Language.id)
            for lang, codes in groupby(q, lambda r: (r[0], r[1], r[2], r[3])):
                res['resources'].append({
                    'id': lang[0],
                    'name': lang[1],
                    'latitude': lang[2],
                    'longitude': lang[3],
                    'identifiers': [
                        {'type': c.type, 'identifier': c.name.lower()
                         if c.type.startswith('WALS') else c.name} for c in codes]})
            return res
        if rsc == 'parameter':
            for id, name in DBSession.query(
                common.Parameter.id,
                common.Parameter.name,
            ).order_by(common.Parameter.pk):
                res['resources'].append({'id': id, 'name': name})
            return res
    return HTTPNotFound()
