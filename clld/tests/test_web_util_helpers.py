from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_link(self):
        from clld.web.util.helpers import link

        link(self.env['request'], common.Language(id='id', name='Name'))

    def test_button(self):
        from clld.web.util.helpers import button

        self.assert_('click' in button('click'))
