# coding: utf8
from __future__ import unicode_literals

from clld.db.models import common


def test_MultiSelect(env):
    from clld.web.util.multiselect import MultiSelect

    ms = MultiSelect(env['request'], common.Language, 'x', url='/')
    ms.render()
    ms.render(selected=[common.Language.first()])
    ms.format_result(common.Language(id='x'))


def test_CombinationMultiSelect(env):
    from clld.web.util.multiselect import CombinationMultiSelect

    ms = CombinationMultiSelect(
        env['request'], combination=common.Combination(common.Parameter.first()))
    ms.render()
