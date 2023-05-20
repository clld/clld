from clld.db.models import common
from clld.interfaces import ILinkAttrs, IFrequencyMarker, IDownload
from clld.web.adapters.download import N3Dump


def test_get_url_template(env):
    from clld.web.util.helpers import get_url_template

    assert get_url_template(env['request'], 'parameter', variable_map={'id': 'ID'}) == '/parameters/{ID}'


def test_newline2br(env):
    from clld.web.util.helpers import newline2br

    assert newline2br(None) == ''


def test_charis_font_spec_css(env):
    from clld.web.util.helpers import charis_font_spec_css

    assert charis_font_spec_css()


def test_collapsed(env):
    from clld.web.util.helpers import collapsed

    collapsed('eid', 'some content')


def test_glottolog_url(env):
    from clld.web.util.helpers import glottolog_url

    glottolog_url('abcd1234')


def test_maybe_license_link(env):
    from clld.web.util.helpers import maybe_license_link

    for i, text in enumerate([
        'no license url',
        'http://example.org/',
        'http://creativecommons.org/licenses/nope/4.0',
        'http://creativecommons.org/licenses/by/4.0',
        'http://en.wikipedia.org/wiki/Public_domain',
    ]):
        maybe_license_link(
            env['request'],
            text,
            button='small' if i else 'none')


def test_get_valueset(request_factory):
    from clld.web.util.helpers import get_valueset

    with request_factory(params=dict(parameter='1')) as req:
        get_valueset(req, common.Language.first())


def test_alt_representations(env):
    from clld.web.util.helpers import alt_representations

    alt_representations(env['request'], common.Parameter.first(), exclude=['xslt'])


def test_icon(env):
    from clld.web.util.helpers import icon

    assert 'white' in icon('download', inverted=True)


def test_link(env, utility_factory, mocker):
    from clld.web.util.helpers import link

    link(env['request'], common.Language(id='id', name='Name'))
    link(env['request'], common.Value.first(), class_='right')

    with utility_factory(mocker.Mock(return_value={}), ILinkAttrs):
        link(env['request'], common.Value.first())


def test_text_citation(env):
    from clld.web.util.helpers import text_citation

    text_citation(env['request'], common.Contribution.first())


def test_get_referents(env):
    from clld.web.util.helpers import get_referents

    get_referents(common.Source.first(), exclude=['language'])


def test_data_uri(env):
    from clld.web.util.helpers import data_uri

    res = data_uri(__file__, 'text/plain')
    assert not res.split(',')[1].startswith("b'")


def test_gbs_link(env, mocker):
    from clld.web.util.helpers import gbs_link

    gbs_link(mocker.MagicMock(), pages='34')
    gbs_link(mocker.MagicMock(jsondata=dict(
        gbs=dict(accessInfo=dict(viewability='NO_PAGES')))))


def test_map_marker_img(env, mocker):
    from clld.web.util.helpers import map_marker_img

    map_marker_img(env['request'], None, marker=mocker.Mock(return_value=None))


def test_maybe_external_link(env):
    from clld.web.util.helpers import maybe_external_link

    assert 'href' not in maybe_external_link('not a URL')
    assert 'href' in maybe_external_link('http://wals.info')


def test_external_link(env):
    from clld.web.util.helpers import external_link

    assert 'http://wals.info' in external_link('http://wals.info')


def test_button(env):
    from clld.web.util.helpers import button

    assert 'click' in button('click')


def test_linked_contributors(env):
    from clld.web.util.helpers import linked_contributors

    linked_contributors(env['request'], common.Contribution.first())


def test_urlescape(env):
    from clld.web.util.helpers import urlescape

    urlescape('a b c\\/ab')


def test_coins(env):
    from clld.web.util.helpers import coins

    coins(env['request'], common.Contribution.first())
    coins(env['request'], None)


def test_format_gbs_identifier(env):
    from clld.web.util.helpers import format_gbs_identifier

    format_gbs_identifier(common.Source.first())


def test_linked_references(env, mocker):
    from clld.web.util.helpers import linked_references

    assert linked_references(env['request'], None) == ''
    mocker.patch('clld.web.util.helpers.link')
    linked_references(
        env['request'],
        mocker.Mock(references=[
            mocker.MagicMock(description=''), mocker.MagicMock(description='')]))


def test_text2html(env):
    from clld.web.util.helpers import text2html

    assert '<br' in text2html('abc\ndef')
    assert 'div' in str(text2html('chunk', mode='p'))


def test_partitioned(env):
    from clld.web.util.helpers import partitioned

    assert list(partitioned(range(10)))[0] == [0, 1, 2, 3]


def test_contactmail(env):
    from clld.web.util.helpers import contactmail

    contactmail(env['request'])


def test_format_frequency(env, mocker, utility_factory):
    from clld.web.util.helpers import format_frequency

    format_frequency(env['request'], common.Value.first())
    format_frequency(env['request'], mocker.Mock(frequency=None))

    with utility_factory(mocker.Mock(return_value='url'), IFrequencyMarker):
        format_frequency(env['request'], common.Value.first())


def test_format_coordinates(env, mocker):
    from clld.web.util.helpers import format_coordinates

    r = str(format_coordinates(mocker.Mock(latitude=5.333333333333, longitude=-9.999)))
    assert "5°20" in r
    assert "10°W" in r
    format_coordinates(mocker.Mock(latitude=5.333, longitude=-9.99), no_seconds=False)
    assert format_coordinates(common.Language.get('l2')) == ''
    assert format_coordinates(common.Language.get('language')) != ''


def test_get_downloads(env, utility_factory):
    from clld.web.util.helpers import get_rdf_dumps, get_downloads

    with utility_factory(N3Dump(common.Language, 'clld'), IDownload):
        assert list(get_rdf_dumps(env['request'], common.Language))
        assert list(get_downloads(env['request']))


def test_rendered_sentence(env, mocker):
    from clld.web.util.helpers import rendered_sentence

    rendered_sentence(mocker.MagicMock())
    rendered_sentence(common.Sentence.first())
    rendered_sentence(common.Sentence.first(), abbrs=dict(SG='singular'))
    assert '1SG' in str(rendered_sentence(common.Sentence.first(), abbrs=dict()))


def test_language_identifier(env):
    from clld.web.util.helpers import language_identifier

    assert language_identifier(None, None) == ''

    lang = common.Language.get('language')
    for identifier in lang.identifiers:
        language_identifier(env['request'], identifier)


def test_localize_url(env):
    from clld.web.util.helpers import localize_url

    assert '__locale__' not in localize_url(env['request'], 'en')
    assert '__locale__=eo' in localize_url(env['request'], 'eo')
    assert '__locale__' not in localize_url(env['request'], 'eo', 'eo')
