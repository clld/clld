from clld.web import datatables
from clld.db.models.common import Language
from clld.tests.util import TestWithEnv


class Tests(TestWithEnv):
    def test_CsvAdapter(self):
        from clld.web.adapters.csv import CsvAdapter

        adapter = CsvAdapter(None)
        adapter.render_to_response(
            datatables.Languages(self.env['request'], Language), self.env['request'])
