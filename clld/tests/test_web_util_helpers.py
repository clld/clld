from mock import Mock, patch

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

    def test_linked_references(self):
        from clld.web.util.helpers import linked_references

        with patch('clld.web.util.helpers.link'):
            linked_references(self.env['request'], Mock(references=[Mock(), Mock()]))

    def test_text2html(self):
        from clld.web.util.helpers import text2html

        self.assertTrue('<br' in text2html('abc\ndef'))

    def test_format_frequency(self):
        from clld.web.util.helpers import format_frequency

        format_frequency(self.env['request'], common.Value.first())
        format_frequency(self.env['request'], Mock(frequency=None))

    def test_rendered_sentence(self):
        from clld.web.util.helpers import rendered_sentence

        rendered_sentence(common.Sentence.first())
        rendered_sentence(common.Sentence.first(), abbrs=dict(SG='singular'))

    def test_language_identifier(self):
        from clld.web.util.helpers import language_identifier

        language_identifier(self.env['request'], Mock(type='x', id='abc'))
        language_identifier(self.env['request'], Mock(type='iso639-3', id='abc'))
        language_identifier(self.env['request'], Mock(type='ethnologue', id='abc'))
