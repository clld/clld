"""Functionality to support reading and writing of excel files."""
from __future__ import unicode_literals, print_function, division, absolute_import

from six.moves import zip
import xlwt

__all__ = ['hyperlink', 'rows']


def hyperlink(url, label=None):
    f = xlwt.Font()
    f.underline = xlwt.Font.UNDERLINE_SINGLE

    style = xlwt.XFStyle()
    style.font = f
    label = label.replace('"', "'") if label else url
    return xlwt.Formula('HYPERLINK("%s";"%s")' % (url, label[:255]))


def rows(sheet, as_dict=False):
    """Read data from an excel sheet.

    :param as_dict:
        If ``True`` rows will be converted to ``dict``s using the content of the first row
        as keys.
    :return: Generator for the rows in the specified sheet.
    """
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
