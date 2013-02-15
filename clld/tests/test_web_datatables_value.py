from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.interfaces import IDataTable


class Tests(TestWithEnv):
    def test_Values(self):
        from clld.web.datatables.value import Values

        dt = Values(self.env['request'], common.Value)
        dt.render()
        self.assertTrue(isinstance(dt.options, dict))
        dt.get_query()

        self.set_request_properties(params={
            'sSearch_0': '> 1',
            'iSortingCols': '1',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc'})

    def test_Values_with_contribution(self):
        from clld.web.datatables.value import Values

        dt = Values(self.env['request'], common.Value, contribution=common.Contribution.first())
        dt.render()
        dt.get_query()

    def test_Values_with_parameter(self):
        from clld.web.datatables.value import Values

        dt = Values(self.env['request'], common.Value, parameter=common.Parameter.first())
        dt.render()
        dt.get_query()
