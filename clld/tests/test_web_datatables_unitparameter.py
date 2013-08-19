from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_Units(self):
        from clld.web.datatables.unitparameter import Unitparameters

        dt = self.handle_dt(Unitparameters, common.UnitParameter)
        self.assertTrue(isinstance(dt.options, dict))
