from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.interfaces import IDataTable


class Tests(TestWithEnv):
    def test_Contributions(self):
        from clld.web.datatables.contribution import Contributions

        dt = Contributions(self.env['request'], common.Contribution)
        dt.render()
        self.assertTrue(isinstance(dt.options, dict))
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)
