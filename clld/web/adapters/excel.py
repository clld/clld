from six.moves import cStringIO as StringIO
from six import PY3
if not PY3:
    import xlwt
else:
    xlwt = None

from clld.web.adapters.base import Index
from clld.lib.excel import hyperlink


class ExcelAdapter(Index):
    extension = 'xls'
    mimetype = 'application/vnd.ms-excel'

    def header(self, ctx, req):
        return ['ID', 'Name']

    def row(self, ctx, req, item):
        return [item.id, hyperlink(req.resource_url(item), item.__unicode__())]

    def render(self, ctx, req):
        if not xlwt:
            return ''
        wb = xlwt.Workbook()
        ws = wb.add_sheet(ctx.__unicode__())

        for i, col in enumerate(self.header(ctx, req)):
            ws.write(0, i, col)

        for j, item in enumerate(ctx.get_query(limit=1000)):
            for i, col in enumerate(self.row(ctx, req, item)):
                ws.write(j + 1, i, col)

        out = StringIO()
        wb.save(out)
        out.seek(0)
        return out.read()

    def render_to_response(self, ctx, req):
        res = super(ExcelAdapter, self).render_to_response(ctx, req)
        res.content_disposition = 'attachment; filename="%s.xls"' % repr(ctx)
        return res


class Values(ExcelAdapter):
    def header(self, ctx, req):
        return super(Values, self).header(ctx, req) + ['Parameter', 'Language']

    def row(self, ctx, req, item):
        res = super(Values, self).row(ctx, req, item)
        for obj in [item.valueset.parameter, item.valueset.language]:
            res.append(hyperlink(req.resource_url(obj), obj.__unicode__()))
        return res
