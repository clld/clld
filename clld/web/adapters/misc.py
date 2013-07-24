from clld.web.adapters.base import Index


class BibtexAdapter(Index):
    extension = 'bib'
    mimetype = 'text/bibtex'

    def render(self, ctx, req):
        return '\n\n'.join(unicode(item.bibtex()) for item in ctx.get_query(limit=1000))
