"""Adapters to render bibliographic information in various formats."""
from clld.web.adapters.base import Representation
from clld.lib.bibtex import IDatabase, IRecord, Database
from clld.interfaces import IIndex, ISource, IDataTable


class Bibtex(Representation):

    """BibTeX.

    .. seealso:: http://en.wikipedia.org/wiki/BibTeX
    """

    extension = 'bib'
    mimetype = 'text/x-bibtex'

    def filename(self, ctx, req):
        return '%s-refs.%s' % (req.dataset.id, self.extension)

    def render_to_response(self, ctx, req):
        res = super(Bibtex, self).render_to_response(ctx, req)
        res.content_disposition = 'attachment; filename="%s"' % self.filename(ctx, req)
        return res

    def render(self, ctx, req):
        if ISource.providedBy(ctx):
            ctx = ctx.bibtex()
        elif IDataTable.providedBy(ctx):
            ctx = Database([s.bibtex() for s in ctx.get_query()])
        return ctx.format(self.extension)


def includeme(config):
    for interface in [IDatabase, IRecord, ISource]:
        config.register_adapter(Bibtex, interface, name=Bibtex.extension)
    config.register_adapter(Bibtex, ISource, IIndex, name=Bibtex.extension)
