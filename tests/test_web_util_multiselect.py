from clld.db.models import common
from clld.web.util.multiselect import *


def test_MultiSelect(env):
    ms = MultiSelect(env['request'], common.Language, 'x', url='/')
    ms.render()
    ms.render(selected=[common.Language.first()])
    ms.format_result(common.Language(id='x'))


def test_CombinationMultiSelect(env):
    ms = CombinationMultiSelect(
        env['request'], combination=common.Combination(common.Parameter.first()))
    ms.render()
