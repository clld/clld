from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_Languages(self):
        from clld.web.datatables.language import Languages

        self.handle_dt(Languages, common.Language)
