# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_Units(self):
        from clld.web.datatables.unitparameter import Unitparameters

        dt = self.handle_dt(Unitparameters, common.UnitParameter)
        self.assertTrue(isinstance(dt.options, dict))
