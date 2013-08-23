from six import PY3
if not PY3:
    import xlwt
else:  # pragma: no cover
    xlwt = None


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
