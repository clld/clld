from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_Contributions(self):
        from clld.web.datatables.contribution import Contributions

        self.handle_dt(Contributions, common.Contribution)
