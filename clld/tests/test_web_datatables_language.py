# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_Languages(self):
        from clld.web.datatables.language import Languages

        self.handle_dt(Languages, common.Language)
