from __future__ import unicode_literals, division, print_function, absolute_import

from six import BytesIO
import xlwt
import xlrd

from clld.lib.excel import *


def test_hyperlink():
    assert hyperlink('http://example.org', label='"example"')


def test_rows():
    wb = xlwt.Workbook()
    ws = wb.add_sheet('1')
    d = {'a': 1}
    ws.write(0, 0, list(d.keys())[0])
    ws.write(1, 0, list(d.values())[0])
    fp = BytesIO()
    wb.save(fp)
    fp.seek(0)
    wb = xlrd.open_workbook(file_contents=fp.read())
    assert list(rows(wb.sheet_by_name('1'), as_dict=True))[0] == d
    assert len(list(rows(wb.sheet_by_name('1')))) == 2
