"""
Serialize clld objects as csv.
"""
import itertools

from csvw.dsv import UnicodeWriter

from clld.web.adapters.base import Index

QUERY_LIMIT = 2000


class CsvAdapter(Index):

    """Represent tables as csv files (maximal %d rows)."""

    __doc__ %= QUERY_LIMIT

    extension = 'csv'
    mimetype = 'text/csv'
    content_type_params = dict(header='present')

    def render(self, ctx, req):
        with UnicodeWriter() as writer:
            rows = iter(ctx.get_query(limit=QUERY_LIMIT))
            first = next(rows, None)
            if first is not None:
                cols = first.csv_head()
                writer.writerow(cols)
                for item in itertools.chain([first], rows):
                    writer.writerow(item.to_csv(ctx=ctx, req=req, cols=cols))
            return writer.read()

    def render_to_response(self, ctx, req):
        res = super(CsvAdapter, self).render_to_response(ctx, req)
        res.content_disposition = 'attachment; filename="%s.csv"' % repr(ctx)
        return res
