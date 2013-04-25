from cStringIO import StringIO

import xlwt


def excel(ctx, req):
    wb = xlwt.Workbook()
    ws = wb.add_sheet(ctx.__unicode__())

    for i, col in enumerate(ctx.cols):
        ws.write(0, i, col.js_args['sTitle'])

    for j, item in enumerate(ctx.get_query(limit=1000)):
        for i, col in enumerate(ctx.cols):
            ws.write(j + 1, i, col.format(item))

    out = StringIO()
    wb.save(out)
    out.seek(0)
    return out.read()


def hyperlink(url, label=None):
    f = xlwt.Font()
    f.underline = xlwt.Font.UNDERLINE_SINGLE

    style = xlwt.XFStyle()
    style.font = f

    return xlwt.Formula('HYPERLINK("%s";"%s")' % (url, label or url))
