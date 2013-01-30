from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.interfaces import IDataTable


class Tests(TestWithEnv):
    def test_DataTable(self):
        from clld.web.datatables.base import DataTable

        dt = DataTable(self.env['request'], common.Parameter)
        col = dt.cols[0]

        dt.render()
        self.assertTrue(isinstance(dt.options, dict))
        dt.get_query()
