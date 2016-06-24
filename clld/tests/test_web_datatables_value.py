# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def _run(self, **kw):
        from clld.web.datatables.value import Values
        return self.handle_dt(Values, common.Value, **kw)

    def test_Values(self):
        dt = self._run()
        self.assertTrue(isinstance(dt.options, dict))

        self.set_request_properties(params={
            'sSearch_0': '> 1',
            'sSearch_1': 's',
            'iSortingCols': '3',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc',
            'iSortCol_1': '1',
            'sSortDir_1': 'desc',
            'iSortCol_2': '2',
            'sSortDir_2': 'desc',
        })
        dt = self._run()

    def test_Values_with_language(self):
        self._run(language=common.Language.first())

    def test_Values_with_contribution(self):
        self._run(contribution=common.Contribution.first())

    def test_Values_with_parameter(self):
        self.set_request_properties(params={'parameter': 'parameter'})
        self._run()
        self.set_request_properties(params={'parameter': 'parameter', 'sSearch_2': 's'})
        self._run()
        self.set_request_properties(params={'parameter': 'no-domain'})
        self._run()
