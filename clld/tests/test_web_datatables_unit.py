from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.interfaces import IDataTable


class Tests(TestWithEnv):
    def test_Units(self):
        from clld.web.datatables.unit import Units

        dt = Units(self.env['request'], common.Unit)
        dt.render()
        self.assertTrue(isinstance(dt.options, dict))
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)

        dt = Units(self.env['request'], common.Unit, language=common.Language.first())
        dt.render()
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)
