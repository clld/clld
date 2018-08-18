"""Functionality to represent clld objects as RDF graphs and serializations."""
from sqlalchemy.orm import load_only
from clldutils.misc import xmlchars

from clld.web.adapters.base import Representation, Index
from clld.lib.rdf import convert


class Rdf(Representation):

    """Virtual base class."""

    rdflibname = None

    def render(self, ctx, req):
        return convert(
            xmlchars(super(Rdf, self).render(ctx, req)), 'xml', self.rdflibname)


class RdfIndex(Index):

    """Basically a rdf sitemap.

    .. note::

        To make this reasonably performant even for large collections of resources,
        we only pass resource ids and names to the template. This may still be not enough -
        think Glottolog refs - in which case the DataTable should implement a suitable
        `rdf_index_query`, e.g. with a LIMIT clause.
    """

    rdflibname = None

    def render(self, ctx, req):
        if req.params.get('sEcho'):
            # triggered from a datatable, thus potentially filtered and sorted
            items = ctx.get_query(limit=1000)
        else:
            # triggered without any filter parameters
            items = ctx.rdf_index_query(req.db.query(ctx.db_model()).order_by(ctx.db_model().pk))
        if isinstance(ctx.model.name, property):
            items = [(item.id, None) for item in items.options(load_only('id'))]
        else:
            items = [(item.id, item.name)
                     for item in items.options(load_only('id', 'name'))]
        return convert(super(RdfIndex, self).render(items, req), 'xml', self.rdflibname)
