from cStringIO import StringIO

from clld.web.adapters.base import Index
from clld.lib.dsv import UnicodeCsvWriter


class CsvAdapter(Index):
    """renders DataTables as csv files
    """
    extension = 'csv'
    mimetype = 'text/csv'

    def render(self, ctx, req):
        out = StringIO()
        writer = UnicodeCsvWriter(out)

        for i, item in enumerate(ctx.get_query(limit=2000)):
            if i == 0:
                cols = item.csv_head()
                writer.writerow(cols)
            writer.writerow(item.to_csv(ctx=ctx, req=req, cols=cols))

        out.seek(0)
        return out.read()

    def render_to_response(self, ctx, req):
        res = super(CsvAdapter, self).render_to_response(ctx, req)
        res.content_disposition = 'attachment; filename="%s.csv"' % repr(ctx)
        return res
