# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.web import datatables
from clld.db.models.common import Language, Value, Sentence
from clld.tests.util import TestWithEnv, WithDbAndDataMixin


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_Languages(self):
        from clld.web.adapters.excel import Languages

        adapter = Languages(None)
        adapter.render_to_response(
            datatables.Languages(self.env['request'], Language), self.env['request'])

    def test_Values(self):
        from clld.web.adapters.excel import Values

        adapter = Values(None)
        adapter.render_to_response(
            datatables.Values(self.env['request'], Value), self.env['request'])

    def test_Sentences(self):
        from clld.web.adapters.excel import Sentences

        adapter = Sentences(None)
        adapter.render_to_response(
            datatables.Sentences(self.env['request'], Sentence), self.env['request'])
