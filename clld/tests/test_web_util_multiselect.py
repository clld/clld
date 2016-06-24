# coding: utf8
from __future__ import unicode_literals

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_MultiSelect(self):
        from clld.web.util.multiselect import MultiSelect

        ms = MultiSelect(self.env['request'], common.Language, 'x', url='/')
        ms.render()
        ms.render(selected=[common.Language.first()])
        ms.format_result(common.Language(id='x'))

    def test_CombinationMultiSelect(self):
        from clld.web.util.multiselect import CombinationMultiSelect

        ms = CombinationMultiSelect(
            self.env['request'], combination=common.Combination(common.Parameter.first()))
        ms.render()
