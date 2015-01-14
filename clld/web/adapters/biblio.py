"""Adapters to render bibliographic information in various formats."""
from clld.web.adapters.base import Representation
from clld.lib.bibtex import IDatabase, IRecord, Database
from clld.interfaces import IIndex, ISource, IDataTable


class _Format(Representation):

    """Virtual base class."""

    def filename(self, ctx, req):
        return '%s-refs.%s' % (req.dataset.id, self.extension)

    def render_to_response(self, ctx, req):
        res = super(_Format, self).render_to_response(ctx, req)
        res.content_disposition = 'attachment; filename="%s"' % self.filename(ctx, req)
        return res

    def render(self, ctx, req):
        if ISource.providedBy(ctx):
            ctx = ctx.bibtex()
        elif IDataTable.providedBy(ctx):
            ctx = Database([s.bibtex() for s in ctx.get_query()])
        return ctx.format(self.extension)


class Bibtex(_Format):

    """BibTeX.

    .. seealso:: http://en.wikipedia.org/wiki/BibTeX
    """

    extension = 'bib'
    mimetype = 'text/x-bibtex'


class Endnote(_Format):

    """Endnote.

    .. seealso:: http://en.wikipedia.org/wiki/EndNote
    """

    extension = 'en'
    mimetype = "application/x-endnote-refer"


class ReferenceManager(_Format):

    """ReferenceManager.

    .. seealso:: http://en.wikipedia.org/wiki/RIS_%28file_format%29
    """

    extension = 'ris'
    mimetype = "application/x-research-info-systems"


class Mods(_Format):

    """Metadata Object Description Schema.

    .. seealso:: http://www.loc.gov/standards/mods/
    """

    extension = 'mods'
    mimetype = 'application/mods+xml'

    def filename(self, ctx, req):
        return '%s-refs.mods.xml' % req.dataset.id


def includeme(config):
    for adapter in [Bibtex, Endnote, ReferenceManager, Mods]:
        for interface in [IDatabase, IRecord, ISource]:
            config.register_adapter(adapter, interface, name=adapter.extension)
        config.register_adapter(
            adapter, ISource, IIndex, name=adapter.extension)
