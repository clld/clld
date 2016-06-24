# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_Contributions(self):
        from clld.web.datatables.contribution import Contributions

        self.handle_dt(Contributions, common.Contribution)
