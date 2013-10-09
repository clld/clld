from six import PY3
if not PY3:
    import xlwt
    import xlrd
else:  # pragma: no cover
    xlwt = None
    xlrd = None


def hyperlink(url, label=None):
    """
    >>> assert hyperlink('http://example.org', label='"example"')
    """
    f = xlwt.Font()
    f.underline = xlwt.Font.UNDERLINE_SINGLE

    style = xlwt.XFStyle()
    style.font = f
    label = label.replace('"', "'") if label else url
    return xlwt.Formula('HYPERLINK("%s";"%s")' % (url, label[:255]))


def rows(sheet, as_dict=False):
    if as_dict:
        # we use the values of the first row as keys:
        keys = [sheet.cell(0, i).value for i in range(sheet.ncols)]
        start = 1
    else:
        start = 0

    for j in range(start, sheet.nrows):
        res = [sheet.cell(j, i).value for i in range(sheet.ncols)]
        if as_dict:
            res = dict(zip(keys, res))
        yield res
