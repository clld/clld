# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_Sources(self):
        from clld.web.datatables.source import Sources

        dt = self.handle_dt(Sources, common.Source)
        self.assertTrue(isinstance(dt.options, dict))

        self.set_request_properties(params={
            'language': 'language',
            'sSearch_5': 'book',
            'iSortingCols': '1',
            'iSortCol_0': '5',
            'sSortDir_0': 'desc'})
        self.handle_dt(Sources, common.Source)

        dt = self.handle_dt(Sources, common.Source, language=common.Language.first())
        self.assertTrue(isinstance(dt.options, dict))
