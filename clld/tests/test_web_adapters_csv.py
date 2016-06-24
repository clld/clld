from __future__ import unicode_literals, division, absolute_import, print_function
import json

from clld.web import datatables
from clld.db.models.common import Language, ValueSet
from clld.tests.util import TestWithEnv, WithDbAndDataMixin


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_CsvAdapter(self):
        from clld.web.adapters.csv import CsvAdapter

        adapter = CsvAdapter(None)
        assert adapter.label
        res = adapter.render(
            datatables.Languages(self.env['request'], Language), self.env['request'])
        self.assert_(res.splitlines())
        self.assert_(adapter.render_to_response(
            datatables.Languages(self.env['request'], Language), self.env['request']))

    def test_CsvwJsonAdapter(self):
        from clld.web.adapters.csv import CsvmJsonAdapter

        adapter = CsvmJsonAdapter(None)
        res = adapter.render(
            datatables.Languages(self.env['request'], Language), self.env['request'])
        self.assertIn('tableSchema', json.loads(res))
        res = adapter.render(
            datatables.Valuesets(self.env['request'], ValueSet), self.env['request'])
        self.assertIn('foreignKeys', json.loads(res)['tableSchema'])
        adapter.render_to_response(
            datatables.Valuesets(self.env['request'], ValueSet), self.env['request'])
