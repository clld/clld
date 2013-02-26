from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_link(self):
        from clld.web.util.helpers import link

        link(self.env['request'], common.Language(id='id', name='Name'))
        link(self.env['request'], common.Value.first())

    def test_external_link(self):
        from clld.web.util.helpers import external_link

        self.assertTrue('http://wals.info' in external_link('http://wals.info'))

    def test_button(self):
        from clld.web.util.helpers import button

        self.assertTrue('click' in button('click'))

    def test_linked_contributors(self):
        from clld.web.util.helpers import linked_contributors

        linked_contributors(self.env['request'], common.Contribution.first())

    def test_text2html(self):
        from clld.web.util.helpers import text2html

        self.assertTrue('<br' in text2html('abc\ndef'))
