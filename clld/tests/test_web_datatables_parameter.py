from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_Parameters(self):
        from clld.web.datatables.parameter import Parameters

        dt = Parameters(self.env['request'], common.Parameter)
        dt.render()
        self.assertTrue(isinstance(dt.options, dict))
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)
