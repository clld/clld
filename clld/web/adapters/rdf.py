"""Functionality to represent clld objects as RDF graphs and serializations."""
from clld.web.adapters.base import Representation, Index
from clld.lib.rdf import convert
from clld.util import xmlchars


class Rdf(Representation):

    """Virtual base class."""

    rdflibname = None

    def render(self, ctx, req):
        return convert(
            xmlchars(super(Rdf, self).render(ctx, req)), 'xml', self.rdflibname)


class RdfIndex(Index):

    """Basically a rdf sitemap.

    .. note::

        To make this reasonably performant even for large collections of resources -
        think glottolog refs - we only pass resource ids to the template.
    """

    rdflibname = None

    def render(self, ctx, req):
        if req.params.get('sEcho'):
            # triggered from a datatable, thus potentially filtered and sorted
            items = [item.id for item in ctx.get_query(limit=1000)]
        else:
            # triggered without any filter parameters
            items = [row[0] for row in req.db.query(ctx.model.id)]
        return convert(super(RdfIndex, self).render(items, req), 'xml', self.rdflibname)
