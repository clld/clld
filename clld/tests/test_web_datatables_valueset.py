# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def _get_dt(self, **kw):
        from clld.web.datatables.valueset import Valuesets

        return self.handle_dt(Valuesets, common.ValueSet, **kw)

    def test_Valuesets(self):
        dt = self._get_dt()
        self.assertTrue(isinstance(dt.options, dict))

        self.set_request_properties(params={
            'sSearch_0': '> 1',
            'sSearch_1': 'x',
            'iSortingCols': '2',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc',
            'iSortCol_1': '1',
            'sSortDir_1': 'desc',
        })
        self._get_dt()

    def test_Valuesets_with_language(self):
        self._get_dt(language=common.Language.first())

    def test_Valuesets_with_contribution(self):
        self._get_dt(contribution=common.Contribution.first())

    def test_Valuesets_with_parameter(self):
        self.set_request_properties(params={'parameter': 'parameter'})
        self._get_dt()
