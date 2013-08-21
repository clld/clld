from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_Values(self):
        from clld.web.datatables.value import Values

        dt = self.handle_dt(Values, common.Value)
        self.assertTrue(isinstance(dt.options, dict))

        self.set_request_properties(params={
            'sSearch_0': '> 1',
            'sSearch_1': 's',
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

        self.handle_dt(Values, common.Value, language=common.Language.first())

    def test_Values_with_contribution(self):
        from clld.web.datatables.value import Values

        self.handle_dt(Values, common.Value, contribution=common.Contribution.first())

    def test_Values_with_parameter(self):
        from clld.web.datatables.value import Values

        self.set_request_properties(params={'parameter': 'parameter'})
        self.handle_dt(Values, common.Value)
        self.set_request_properties(params={'parameter': 'parameter', 'sSearch_2': 's'})
        self.handle_dt(Values, common.Value)
        self.set_request_properties(params={'parameter': 'no-domain'})
        self.handle_dt(Values, common.Value)
