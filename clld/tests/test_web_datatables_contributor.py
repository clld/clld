from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.interfaces import IDataTable


class Tests(TestWithEnv):
    def test_Contributors(self):
        from clld.web.datatables.contributor import Contributors

        self.set_request_properties(params={
            'iSortingCols': '1',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc'})

        dt = Contributors(self.env['request'], common.Contributor)
        dt.render()
        self.assertTrue(isinstance(dt.options, dict))
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)
