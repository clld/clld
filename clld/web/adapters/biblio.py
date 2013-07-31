"""Adapters to render bibtex
"""
from clld.web.adapters.base import Representation
from clld.lib.bibtex import IDatabase, IRecord, Database
from clld.interfaces import IRepresentation, IIndex, ISource, IDataTable


class _Format(Representation):
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
    extension = 'bib'
    mimetype = 'text/x-bibtex'


class Endnote(_Format):
    extension = 'en'
    mimetype = "application/x-endnote-refer"


class ReferenceManager(_Format):
    extension = 'ris'
    mimetype = "application/x-research-info-systems"


class Mods(_Format):
    extension = 'mods'
    mimetype = 'application/mods+xml'

    def filename(self, ctx, req):
        return '%s-refs.mods.xml' % req.dataset.id


def includeme(config):
    for adapter in [Bibtex, Endnote, ReferenceManager, Mods]:
        for interface in [IDatabase, IRecord, ISource]:
            config.registry.registerAdapter(
                adapter, (interface,), IRepresentation, name=adapter.extension)
        config.registry.registerAdapter(
            adapter, (ISource,), IIndex, name=adapter.extension)
