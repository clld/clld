from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.interfaces import IDataTable


class Tests(TestWithEnv):
    def test_Languages(self):
        from clld.web.datatables.language import Languages

        dt = Languages(self.env['request'], common.Language)
        dt.render()
        self.assertTrue(isinstance(dt.options, dict))
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)
