from __future__ import unicode_literals, division, absolute_import, print_function

from clld.web import datatables
from clld.db.models.common import Language
from clld.tests.util import TestWithEnv


class Tests(TestWithEnv):
    def test_CsvAdapter(self):
        from clld.web.adapters.csv import CsvAdapter

        adapter = CsvAdapter(None)
        res = adapter.render(
            datatables.Languages(self.env['request'], Language), self.env['request'])
        self.assert_(res.splitlines())
        self.assert_(adapter.render_to_response(
            datatables.Languages(self.env['request'], Language), self.env['request']))
