from six.moves import cStringIO as StringIO
from six import PY3
if not PY3:
    import xlwt
else:  # pragma: no cover
    xlwt = None

from clld.web.adapters.base import Index
from clld.lib.excel import hyperlink


class ExcelAdapter(Index):
    """renders DataTables as excel sheets
    """
    extension = 'xls'
    mimetype = 'application/vnd.ms-excel'

    def header(self, ctx, req):
        return ['ID', 'Name']

    def row(self, ctx, req, item):
        return [item.id, hyperlink(req.resource_url(item), item.__unicode__())]

    def render(self, ctx, req):
        if not xlwt:
            return ''  # pragma: no cover
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


class Languages(ExcelAdapter):
    def header(self, ctx, req):
        return super(Languages, self).header(ctx, req) + ['Latitude', 'Longitude']

    def row(self, ctx, req, item):
        res = super(Languages, self).row(ctx, req, item)
        res.extend([item.latitude, item.longitude])
        return res


class Values(ExcelAdapter):
    def header(self, ctx, req):
        return super(Values, self).header(ctx, req) + [
            'Parameter', 'Language', 'Frequency', 'Confidence', 'References']

    def row(self, ctx, req, item):
        res = super(Values, self).row(ctx, req, item)
        for obj in [item.valueset.parameter, item.valueset.language]:
            res.append(hyperlink(req.resource_url(obj), obj.__unicode__()))
        res.extend([item.frequency or '', item.confidence or ''])
        res.append(';'.join(filter(
            None, [r.source.name for r in item.valueset.references if r.source])))
        return res


class Sentences(ExcelAdapter):
    def header(self, ctx, req):
        return ['ID', 'Text', 'Analyzed', 'Gloss', 'Translation', 'Language']

    def row(self, ctx, req, item):
        return [
            hyperlink(req.resource_url(item), item.id),
            item.name,
            item.analyzed,
            item.gloss,
            item.description,
            hyperlink(req.resource_url(item.language), item.language.name),
        ]
