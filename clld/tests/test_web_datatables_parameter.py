# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_Parameters(self):
        from clld.web.datatables.parameter import Parameters

        self.handle_dt(Parameters, common.Parameter)
