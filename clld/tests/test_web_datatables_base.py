from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_DataTable(self):
        from clld.web.datatables.base import (
            DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol,
        )

        class TestTable(DataTable):
            def col_defs(self):
                return [
                    Col(self, 'pk'),
                    DetailsRowLinkCol(self),
                    LinkToMapCol(self),
                    LinkCol(self, 'link')]

        dt = TestTable(self.env['request'], common.Contributor)
        assert dt.cols[0]

        dt.render()
        self.assertTrue(isinstance(dt.options, dict))
        dt.get_query()

        self.set_request_properties(params={
            'sSearch_0': '> 1',
            'iSortingCols': '1',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc'})
        dt = TestTable(self.env['request'], common.Contributor)
        dt.get_query()
