# coding: utf8
from __future__ import unicode_literals

from mock import Mock, patch, MagicMock
from six import text_type

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common
from clld.interfaces import ILinkAttrs, IFrequencyMarker, IDownload
from clld.web.adapters.download import N3Dump


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_get_url_template(self):
        from clld.web.util.helpers import get_url_template

        self.assertEqual(
            get_url_template(self.env['request'], 'parameter', variable_map={'id': 'ID'}),
            '/parameters/{ID}')

    def test_newline2br(self):
        from clld.web.util.helpers import newline2br

        self.assertEqual(newline2br(None), '')

    def test_charis_font_spec_css(self):
        from clld.web.util.helpers import charis_font_spec_css

        assert charis_font_spec_css()

    def test_collapsed(self):
        from clld.web.util.helpers import collapsed

        collapsed('eid', 'some content')

    def test_glottolog_url(self):
        from clld.web.util.helpers import glottolog_url

        glottolog_url('abcd1234')

    def test_maybe_license_link(self):
        from clld.web.util.helpers import maybe_license_link

        for i, text in enumerate([
            'no license url',
            'http://example.org/',
            'http://creativecommons.org/licenses/nope/4.0',
            'http://creativecommons.org/licenses/by/4.0',
            'http://en.wikipedia.org/wiki/Public_domain',
        ]):
            maybe_license_link(
                self.env['request'],
                text,
                button='small' if i else 'none')

    def test_get_valueset(self):
        from clld.web.util.helpers import get_valueset

        self.set_request_properties(params=dict(parameter='1'))
        get_valueset(self.env['request'], common.Language.first())

    def test_alt_representations(self):
        from clld.web.util.helpers import alt_representations

        alt_representations(
            self.env['request'], common.Parameter.first(), exclude=['xslt'])

    def test_icon(self):
        from clld.web.util.helpers import icon

        self.assertIn('white', icon('download', inverted=True))

    def test_icons(self):
        from clld.web.util.helpers import icons

        self.assert_(icons(self.env['request'], 'param'))

    def test_link(self):
        from clld.web.util.helpers import link

        link(self.env['request'], common.Language(id='id', name='Name'))
        link(self.env['request'], common.Value.first(), class_='right')

        with self.utility(Mock(return_value={}), ILinkAttrs):
            link(self.env['request'], common.Value.first())

    def test_text_citation(self):
        from clld.web.util.helpers import text_citation

        text_citation(self.env['request'], common.Contribution.first())

    def test_get_referents(self):
        from clld.web.util.helpers import get_referents

        get_referents(common.Source.first(), exclude=['language'])

    def test_data_uri(self):
        from clld.web.util.helpers import data_uri

        res = data_uri(__file__, 'text/plain')
        self.assertFalse(res.split(',')[1].startswith("b'"))

    def test_gbs_link(self):
        from clld.web.util.helpers import gbs_link

        gbs_link(MagicMock(), pages='34')
        gbs_link(MagicMock(jsondata=dict(
            gbs=dict(accessInfo=dict(viewability='NO_PAGES')))))

    def test_map_marker_img(self):
        from clld.web.util.helpers import map_marker_img

        map_marker_img(self.env['request'], None, marker=Mock(return_value=None))

    def test_maybe_external_link(self):
        from clld.web.util.helpers import maybe_external_link

        self.assertFalse('href' in maybe_external_link('not a URL'))
        self.assertTrue('href' in maybe_external_link('http://wals.info'))

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

        self.assertEqual(linked_references(self.env['request'], None), '')
        with patch('clld.web.util.helpers.link'):
            linked_references(
                self.env['request'], Mock(
                    references=[MagicMock(description=''), MagicMock(description='')]))

    def test_text2html(self):
        from clld.web.util.helpers import text2html

        self.assertTrue('<br' in text2html('abc\ndef'))
        self.assertIn('div', text_type(text2html('chunk', mode='p')))

    def test_partitioned(self):
        from clld.web.util.helpers import partitioned

        self.assertEqual(list(partitioned(range(10)))[0], [0, 1, 2, 3])

    def test_contactmail(self):
        from clld.web.util.helpers import contactmail

        contactmail(self.env['request'])

    def test_format_frequency(self):
        from clld.web.util.helpers import format_frequency

        format_frequency(self.env['request'], common.Value.first())
        format_frequency(self.env['request'], Mock(frequency=None))

        with self.utility(Mock(return_value='url'), IFrequencyMarker):
            format_frequency(self.env['request'], common.Value.first())

    def test_format_coordinates(self):
        from clld.web.util.helpers import format_coordinates

        r = text_type(format_coordinates(Mock(latitude=5.333333333333, longitude=-9.999)))
        assert "5°20" in r
        assert "10°W" in r
        format_coordinates(Mock(latitude=5.333, longitude=-9.99), no_seconds=False)
        assert format_coordinates(common.Language.get('l2')) == ''
        assert format_coordinates(common.Language.get('language')) != ''

    def test_get_downloads(self):
        from clld.web.util.helpers import get_rdf_dumps, get_downloads

        with self.utility(N3Dump(common.Language, 'clld'), IDownload):
            assert list(get_rdf_dumps(self.env['request'], common.Language))
            assert list(get_downloads(self.env['request']))

    def test_rendered_sentence(self):
        from clld.web.util.helpers import rendered_sentence

        rendered_sentence(MagicMock())
        rendered_sentence(common.Sentence.first())
        rendered_sentence(common.Sentence.first(), abbrs=dict(SG='singular'))

    def test_language_identifier(self):
        from clld.web.util.helpers import language_identifier

        assert language_identifier(None, None) == ''
        for identifier in common.Language.get('language').identifiers:
            language_identifier(self.env['request'], identifier)
