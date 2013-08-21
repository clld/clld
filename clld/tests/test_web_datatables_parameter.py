from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_Parameters(self):
        from clld.web.datatables.parameter import Parameters

        self.handle_dt(Parameters, common.Parameter)
