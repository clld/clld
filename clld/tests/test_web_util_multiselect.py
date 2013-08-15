from mock import Mock, patch, MagicMock

from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_MultiSelect(self):
        from clld.web.util.multiselect import MultiSelect

        ms = MultiSelect(self.env['request'], common.Language, 'x', url='/')
        ms.render()
        ms.format_result(common.Language(id='x'))
