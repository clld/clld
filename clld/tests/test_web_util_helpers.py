from mock import Mock, patch, MagicMock

from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.interfaces import ILinkAttrs, IFrequencyMarker, IDownload
from clld.web.adapters.download import N3Dump


class Tests(TestWithEnv):
    def test_link(self):
        from clld.web.util.helpers import link

        link(self.env['request'], common.Language(id='id', name='Name'))
        link(self.env['request'], common.Value.first())

        with self.utility(Mock(return_value={}), ILinkAttrs):
            link(self.env['request'], common.Value.first())

    def test_gbs_link(self):
        from clld.web.util.helpers import gbs_link

        gbs_link(MagicMock(), pages='34')
        gbs_link(MagicMock(jsondata=dict(gbs=dict(accessInfo=dict(viewability='NO_PAGES')))))

    def test_map_marker_img(self):
        from clld.web.util.helpers import map_marker_img

        map_marker_img(self.env['request'], None, marker=Mock(return_value=None))

    def test_get_downloads(self):
        from clld.web.util.helpers import get_downloads

        list(get_downloads(self.env['request']))

    def test_get_rdf_dumps(self):
        from clld.web.util.helpers import get_rdf_dumps

        list(get_rdf_dumps(self.env['request'], common.Language))

    def test_external_link(self):
        from clld.web.util.helpers import external_link

        self.assertTrue('http://wals.info' in external_link('http://wals.info'))

    def test_button(self):
        from clld.web.util.helpers import button

        self.assertTrue('click' in button('click'))

    def test_linked_contributors(self):
        from clld.web.util.helpers import linked_contributors

        linked_contributors(self.env['request'], common.Contribution.first())

    def test_urlescape(self):
        from clld.web.util.helpers import urlescape

        urlescape('a b c\\/ab')

    def test_coins(self):
        from clld.web.util.helpers import coins

        coins(self.env['request'], common.Contribution.first())
        coins(self.env['request'], None)

    def test_format_gbs_identifier(self):
        from clld.web.util.helpers import format_gbs_identifier

        format_gbs_identifier(common.Source.first())

    def test_linked_references(self):
        from clld.web.util.helpers import linked_references

        with patch('clld.web.util.helpers.link'):
            linked_references(
                self.env['request'], Mock(
                    references=[MagicMock(description=''), MagicMock(description='')]))

    def test_text2html(self):
        from clld.web.util.helpers import text2html

        self.assertTrue('<br' in text2html('abc\ndef'))

    def test_contactmail(self):
        from clld.web.util.helpers import contactmail

        contactmail(self.env['request'])

    def test_format_frequency(self):
        from clld.web.util.helpers import format_frequency

        format_frequency(self.env['request'], common.Value.first())
        format_frequency(self.env['request'], Mock(frequency=None))

        with self.utility(Mock(return_value='url'), IFrequencyMarker):
            format_frequency(self.env['request'], common.Value.first())

    def test_get_rdf_dumps(self):
        from clld.web.util.helpers import get_rdf_dumps

        with self.utility(N3Dump(common.Language, 'clld'), IDownload):
            assert list(get_rdf_dumps(self.env['request'], common.Language))

    def test_rendered_sentence(self):
        from clld.web.util.helpers import rendered_sentence

        rendered_sentence(MagicMock())
        rendered_sentence(common.Sentence.first())
        rendered_sentence(common.Sentence.first(), abbrs=dict(SG='singular'))

    def test_language_identifier(self):
        from clld.web.util.helpers import language_identifier

        language_identifier(self.env['request'], Mock(type='x', id='abc'))
        language_identifier(self.env['request'], Mock(type='iso639-3', id='abc'))
        language_identifier(self.env['request'], Mock(type='ethnologue', id='abc'))
