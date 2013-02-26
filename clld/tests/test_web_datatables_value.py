from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.interfaces import IDataTable


class Tests(TestWithEnv):
    def test_Values(self):
        from clld.web.datatables.value import Values

        dt = Values(self.env['request'], common.Value)
        dt.render()
        self.assertTrue(isinstance(dt.options, dict))
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)

        self.set_request_properties(params={
            'sSearch_0': '> 1',
            'iSortingCols': '3',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc',
            'iSortCol_1': '1',
            'sSortDir_1': 'desc',
            'iSortCol_2': '2',
            'sSortDir_2': 'desc',
            })
        dt = Values(self.env['request'], common.Value)
        dt.get_query()

    def test_Values_with_language(self):
        from clld.web.datatables.value import Values

        dt = Values(self.env['request'], common.Value, language=common.Language.first())
        dt.render()
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)

    def test_Values_with_contribution(self):
        from clld.web.datatables.value import Values

        dt = Values(self.env['request'], common.Value, contribution=common.Contribution.first())
        dt.render()
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)

    def test_Values_with_parameter(self):
        from clld.web.datatables.value import Values

        self.set_request_properties(params={'parameter': 'p'})
        dt = Values(self.env['request'], common.Value)
        dt.render()
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)
