"""Various helper functions to be used mainly in templates.

.. note:: This module is available within Mako templates as ``h``.
"""
import os
import re
from itertools import groupby  # we just import this to have it available in templates!
import datetime  # we just import this to have it available in templates!
from base64 import b64encode
from math import floor
from urllib.parse import quote, urlencode

from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from markupsafe import Markup
from pyramid.renderers import render as pyramid_render
from pyramid.threadlocal import get_current_request
from pyramid.interfaces import IRoutesMapper
from purl import URL
from zope.interface import providedBy
from clldutils.misc import xmlchars

import clld
from clld import interfaces
from clld import RESOURCES
from clld.web.util.htmllib import HTML, literal
from clld.web.util.downloadwidget import DownloadWidget
from clld.db.meta import DBSession
from clld.db.models import common as models
from clld.web.adapters import get_adapter, get_adapters
from clld.lib.coins import ContextObject
from clld.lib import bibtex
from clld.lib import rdf

# appease pyflakes
assert get_adapter
assert get_adapters
assert get_current_request
assert datetime
assert xmlchars
assert groupby

#: dimension of marker images on maps, legends and in datatables.
MARKER_IMG_DIM = '20'


def cc_link(req, license_url, button='regular'):
    if license_url == 'https://en.wikipedia.org/wiki/Public_domain':
        license_url = 'https://creativecommons.org/publicdomain/zero/1.0/'  # pragma: no cover
    license_url = URL(license_url)
    if license_url.host() != 'creativecommons.org':
        return

    comps = license_url.path().split('/')
    if len(comps) < 3:
        return  # pragma: no cover

    known = {
        'zero': 'Public Domain',
        'by': 'Creative Commons Attribution License',
        'by-nc': 'Creative Commons Attribution-NonCommercial License',
        'by-nc-nd': 'Creative Commons Attribution-NonCommercial-NoDerivatives License',
        'by-nc-sa': 'Creative Commons Attribution-NonCommercial-ShareAlike License',
        'by-nd': 'Creative Commons Attribution-NoDerivatives License',
        'by-sa': 'Creative Commons Attribution-ShareAlike License'}
    if comps[2] not in known:
        return

    icon = 'cc-' + comps[2] + ('-small' if button == 'small' else '') + '.png'
    img_attrs = dict(
        alt=known[comps[2]],
        src=req.static_url('clld:web/static/images/' + icon))
    height, width = (15, 80) if button == 'small' else (30, 86)
    img_attrs.update(height=height, width=width)
    return HTML.a(HTML.img(**img_attrs), href=license_url, rel='license')


def maybe_license_link(req, license, **kw):
    cc_link_ = cc_link(req, license, button=kw.pop('button', 'regular'))
    if cc_link_:
        return cc_link_
    license_url = URL(license)
    if license_url.host():
        return external_link(license_url, **kw)
    return license


def get_valueset(req, ctx):
    param = req.params.get('parameter')
    if param is None:  # pragma: no cover
        return

    try:
        param = int(param)
    except ValueError:  # pragma: no cover
        pass

    query = DBSession.query(models.ValueSet)\
        .filter(models.ValueSet.language_pk == ctx.pk)

    if isinstance(param, int):
        query = query.filter(models.ValueSet.parameter_pk == param)
    else:  # pragma: no cover
        query = query.join(models.Parameter).filter(models.Parameter.id == param)

    return query.first()


def get_url_template(req, route, relative=True, variable_map=None):
    variable_map = variable_map or {}
    if isinstance(route, str):
        route = req.registry.getUtility(IRoutesMapper).get_route(route)
    if route:
        res = '' if relative else req.application_url
        param_pattern = re.compile(r'\{(?P<name>[a-z]+)(:[^\}]+)?\}')
        return res + param_pattern.sub(
            lambda m: '{%s}' % variable_map.get(m.group('name'), m.group('name')),
            route.pattern)


def rdf_namespace_attrs():
    return '\n'.join('xmlns:%s="%s"' % item for item in rdf.NAMESPACES.items())


def urlescape(string):
    return quote(string, safe='')


def dumps(obj):
    return JS.sub(pyramid_render('json', obj))


def data_uri(filename, mimetype):
    with open(filename, mode='rb') as fp:
        content = fp.read()
    return 'data:%s;base64,%s' % (mimetype, b64encode(content).decode())


class JS(object):

    """Markup JavaScript object names for proper serialization to pseudo-JSON.

    We use JSON serialization to convert python objects to javascript objects, e.g. for
    options. Sometimes these options take javascript names (of functions, etc.). To make
    sure such names can be serialized properly, i.e. without being quoted as literal
    strings, they can be wrapped into a JS object.
    """

    delimiter = '|'
    pattern = re.compile(r'\"\{0}(?P<name>[^\{0}]+)\{0}\"'.format(delimiter))

    def __init__(self, name):
        self.name = name

    def __call__(self, *args):
        return '%s(%s)' % (self.name, ', '.join(
            arg.name if isinstance(arg, JS) else dumps(arg) for arg in args))

    def __getattr__(self, attr):
        return JS('%s.%s' % (self.name, attr))

    def __json__(self, request=None):
        return '{0}{1}{0}'.format(self.delimiter, self.name)

    @classmethod
    def sub(self, string):
        return self.pattern.sub(lambda m: m.group('name'), string)


JSFeed = JS('CLLD.Feed')
JSMap = JS('CLLD.map')
JSModal = JS('CLLD.Modal')
JSDataTable = JS('CLLD.DataTable')


class JSNamespace(object):

    """Shortcut to create JS objects within a common namespace."""

    def __init__(self, prefix):
        self.prefix = prefix

    def __getattr__(self, name):
        return JS(self.prefix + '.' + name)


JS_CLLD = JSNamespace('CLLD')


def text_citation(req, ctx):
    citation = get_adapter(interfaces.IRepresentation, ctx, req, ext='md.txt')
    return citation.render(ctx, req)


def get_downloads(req):
    for k, items in groupby(
        sorted(
            list(req.registry.getUtilitiesFor(interfaces.IDownload)), key=lambda t: t[0]),
        lambda t: t[1].model.__name__ + 's',
    ):
        yield k, sorted([i[1] for i in items if i[1].size], key=lambda d: d.ext)


def get_rdf_dumps(req, model):
    rdf_exts = [n.extension for n in rdf.FORMATS.values()]
    for name, dl in req.registry.getUtilitiesFor(interfaces.IDownload):
        if dl.model == model and dl.ext in rdf_exts:
            yield dl


def coins(req, obj, label=''):
    if not isinstance(obj, bibtex.Record):
        adapter = get_adapter(interfaces.IMetadata, obj, req, ext='md.bib')
        if not adapter:
            return label
        obj = adapter.rec(obj, req)
    co = ContextObject.from_bibtex('clld', obj)
    return HTML.span(label, **co.span_attrs())


def format_gbs_identifier(source):
    return source.gbs_identifier.replace(':', '-') if source.gbs_identifier else source.pk


def format_coordinates(obj, no_seconds=True, wgs_link=True):
    """Format WGS84 coordinates as HTML.

    .. seealso:: https://en.wikipedia.org/wiki/ISO_6709#Order.2C_sign.2C_and_units
    """
    def degminsec(dec, hemispheres):
        _dec = abs(dec)
        degrees = int(floor(_dec))
        _dec = (_dec - int(floor(_dec))) * 60
        minutes = int(floor(_dec))
        _dec = (_dec - int(floor(_dec))) * 60
        seconds = _dec
        if no_seconds:
            if seconds > 30:
                if minutes < 59:
                    minutes += 1
                else:
                    minutes = 0
                    degrees += 1
        fmt = "{0}\xb0"
        if minutes:
            fmt += "{1:0>2d}'"
        if not no_seconds and seconds:
            fmt += '{2:0>2f}"'
        fmt += hemispheres[0] if dec > 0 else hemispheres[1]
        return str(fmt).format(degrees, minutes, seconds)

    if not isinstance(obj.latitude, float) or not isinstance(obj.longitude, float):
        return ''
    return HTML.div(
        HTML.table(
            HTML.tr(
                HTML.td(
                    'Coordinates ',
                    external_link(
                        'https://en.wikipedia.org/wiki/World_Geodetic_System_1984',
                        label="WGS84") if wgs_link else ''),
                HTML.td(
                    HTML.span('%s, %s' % (
                        degminsec(obj.latitude, 'NS'), degminsec(obj.longitude, 'EW'))),
                    HTML.br(),
                    HTML.span(
                        '{0.latitude:.2f}, {0.longitude:.2f}'.format(obj),
                        class_='geo'))),
            class_="table table-condensed"))


def format_license_icon_url(req):
    if 'license_icon' in req.dataset.jsondata:
        url = req.dataset.jsondata['license_icon']
        if not url.startswith('http'):
            url = req.static_url('clld:web/static/images/' + url)
        return url


def format_frequency(req, obj, marker=None, height=MARKER_IMG_DIM, width=MARKER_IMG_DIM):
    if not obj.frequency or obj.frequency == 100:
        return ''
    res = 'Frequency: %s%%' % round(obj.frequency, 1)
    marker = marker or req.registry.queryUtility(interfaces.IFrequencyMarker)
    if marker:
        url = marker(obj, req)
        if url:
            return marker_img(url, height=height, width=width, alt=res, title=res)
    return res


def map_marker_url(req, obj, marker=None):
    marker = marker or req.registry.getUtility(interfaces.IMapMarker)
    return marker(obj, req)


def map_marker_img(req, obj, marker=None, height=MARKER_IMG_DIM, width=MARKER_IMG_DIM):
    url = map_marker_url(req, obj, marker=marker)
    if url:
        return marker_img(url, height=height, width=width)
    return ''


def link(req, obj, **kw):
    get_link_attrs = req.registry.queryUtility(interfaces.ILinkAttrs)
    if get_link_attrs:
        kw = get_link_attrs(req, obj, **kw)

    if 'class_' in kw:
        kw['class'] = kw['class_']
        del kw['class_']

    rsc = None
    rsc_name = kw.pop('rsc', None)
    for _rsc in RESOURCES:
        if _rsc.interface.providedBy(obj) or _rsc.name == rsc_name:
            rsc = _rsc
            break
    assert rsc
    href = kw.pop('href', req.resource_url(obj, rsc=rsc, **kw.pop('url_kw', {})))
    kw['class'] = ' '.join(
        filter(None, kw.get('class', '').split() + [rsc.interface.__name__[1:]]))
    label = kw.pop('label', str(obj))
    kw.setdefault('title', label)
    return HTML.a(label, href=href, **kw)


def external_link(url, label=None, inverted=False, **kw):
    kw.setdefault('title', label or url)
    kw.setdefault('href', url)
    return HTML.a(icon('share', inverted=inverted), ' ', label or url, **kw)


def maybe_external_link(text, **kw):
    url = URL(text)
    if url.host() and url.scheme() in ['http', 'https']:
        return external_link(text, **kw)
    return text


def link_to_map(language):
    return HTML.a(
        icon('icon-globe'),
        title='show %s on map' % language.name,
        href="#map",
        onclick=JS_CLLD.mapShowInfoWindow(None, language.id))


def gbs_link(source, pages=None):
    """Format Google-Books information for source as HTML."""
    if not source or not source.google_book_search_id or not source.jsondata.get('gbs'):
        return ''
    if source.jsondata['gbs']['accessInfo']['viewability'] in ['NO_PAGES']:
        return ''
    pg = 'PP1'
    if pages:
        match = re.search('(?P<startpage>[0-9]+)', pages)
        if match:
            pg = 'PA' + match.group('startpage')
    return HTML.a(
        HTML.img(src="https://www.google.com/intl/en/googlebooks/images/"
                 "gbs_preview_button1.gif"),
        href="https://books.google.com/books?id=%s&lpg=PP1&pg=%s" % (
            source.google_book_search_id, pg)
    )


def button(*content, **attrs):
    tag = attrs.pop('tag', HTML.a if 'href' in attrs else HTML.button)
    attrs.setdefault('type', 'button')
    class_ = attrs['class'] if 'class' in attrs else attrs.pop('class_', '').split()
    if 'btn' not in class_:
        class_.append('btn')
    attrs['class'] = ' '.join(class_)
    return tag(*content, **attrs)


def cite_button(req, ctx):
    return button(
        'cite',
        id="cite-button-%s" % ctx.id,
        onclick=JSModal.show(ctx.name, req.resource_url(ctx, ext='md.html')))


# regex to match standard abbreviations in gloss units:
# We look for sequences of uppercase letters which are not followed by a lowercase letter.
GLOSS_ABBR_PATTERN = re.compile(
    '(?P<personprefix>1|2|3)?(?P<abbr>[A-Z]+)(?P<personsuffix>1|2|3)?(?=([^a-z]|$))')
ALT_TRANSLATION_LANGUAGE_PATTERN = re.compile(r'((?P<language>[a-zA-Z\s]+):)')


#
# TODO: enumerate exceptions: 1SG, 2SG, 3SG, ?PL, ?DU
#
def rendered_sentence(sentence, abbrs=None, fmt='long'):
    """Format a sentence as HTML."""
    if sentence.xhtml:
        return HTML.div(
            HTML.div(Markup(sentence.xhtml), class_='body'), class_="sentence")

    if abbrs is None:
        q = DBSession.query(models.GlossAbbreviation).filter(
            or_(models.GlossAbbreviation.language_pk == sentence.language_pk,
                models.GlossAbbreviation.language_pk == None)
        )
        abbrs = dict((g.id, g.name) for g in q)

    def gloss_with_tooltip(gloss):
        person_map = {
            '1': 'first person',
            '2': 'second person',
            '3': 'third person',
        }

        res = []
        end = 0
        for match in GLOSS_ABBR_PATTERN.finditer(gloss):
            if match.start() > end:
                res.append(gloss[end:match.start()])

            abbr = match.group('abbr')
            if abbr in abbrs:
                explanation = abbrs[abbr]
                if match.group('personprefix'):
                    explanation = '%s %s' % (
                        person_map[match.group('personprefix')], explanation)

                if match.group('personsuffix'):
                    explanation = '%s %s' % (
                        explanation, person_map[match.group('personsuffix')])

                res.append(HTML.span(
                    HTML.span(gloss[match.start():match.end()].lower(), class_='sc'),
                    **{'data-hint': explanation, 'class': 'hint--bottom'}))
            else:
                res.append(abbr)

            end = match.end()

        res.append(gloss[end:])
        return filter(None, res)

    def alt_translation(sentence):
        res = ''
        if sentence.jsondata.get('alt_translation'):
            text = sentence.jsondata['alt_translation']
            name = ''
            if ALT_TRANSLATION_LANGUAGE_PATTERN.match(text):
                name, text = [t.strip() for t in text.split(':', 1)]
                name = HTML.span(name + ': ')
            res = HTML.div(name, HTML.span(text, class_='translation'))
        return res

    units = []
    if sentence.analyzed and sentence.gloss:
        analyzed = sentence.analyzed
        glossed = sentence.gloss
        for morpheme, gloss in zip(analyzed.split('\t'), glossed.split('\t')):
            units.append(HTML.div(
                HTML.div(morpheme, class_='morpheme'),
                HTML.div(*gloss_with_tooltip(gloss), **{'class': 'gloss'}),
                class_='gloss-unit'))

    return HTML.div(
        HTML.div(
            HTML.div(
                HTML.div(sentence.original_script, class_='original-script')
                if sentence.original_script else '',
                HTML.div(literal(sentence.markup_text or sentence.name),
                         class_='object-language'),
                HTML.div(*units, **{'class': 'gloss-box'}) if units else '',
                HTML.div(sentence.description, class_='translation')
                if sentence.description else '',
                alt_translation(sentence),
                class_='body',
            ),
            class_="sentence",
        ),
        class_="sentence-wrapper",
    )


def icon(class_, inverted=False, **kw):
    if not class_.startswith('icon-'):
        class_ = 'icon-' + class_
    if inverted:
        class_ = '%s icon-white' % class_
    return HTML.i(class_=class_, **kw)


def contactmail(req, ctx=None, title='contact maintainer'):
    """Format the contact address for a dataset as mailto: link."""
    params = {}
    for name in ['subject', 'body']:
        params[name] = pyramid_render(
            'contactmail_{0}.mako'.format(name), {'req': req, 'ctx': ctx}, request=req)\
            .strip()\
            .encode('utf8')
        query = urlencode(params).replace('+', '%20')
    href = 'mailto:{0}?{1}'.format(req.dataset.contact, query)
    return button(icon('bell'), title=title, href=href, class_='btn-warning btn-mini')


def newline2br(text):
    """Replace newlines in text with HTML br tags."""
    if not text:
        return ''
    chunks = []
    for i, line in enumerate(text.split('\n')):
        if i > 0:
            chunks.append(HTML.br())
        chunks.append(literal(line))
    return '\n'.join(chunks)


def text2html(text, mode='br', sep='\n\n'):
    """Turn plain text into simple HTML."""
    if mode == 'p':
        return HTML.div(*[HTML.p(literal(newline2br(line))) for line in text.split(sep)])
    return HTML.p(literal(newline2br(text)))


def linked_contributors(req, contribution):
    chunks = []
    for i, c in enumerate(contribution.primary_contributors):
        if i > 0:
            chunks.append(' and ')
        chunks.append(link(req, c))

    for i, c in enumerate(contribution.secondary_contributors):
        if i == 0 and contribution.primary_contributors:
            chunks.append(' with ')
        if i > 0:
            chunks.append(' and ')
        chunks.append(link(req, c))

    return HTML.span(*chunks)


def linked_references(req, obj):
    chunks = []
    for i, ref in enumerate(getattr(obj, 'references', [])):
        if ref.source:
            gbs = gbs_link(ref.source, pages=ref.description)
            if i > 0:
                chunks.append('; ')
            chunks.append(HTML.span(
                link(req, ref.source),
                HTML.span(
                    ': %s' % ref.description if ref.description else '',
                    class_='pages'),
                ' ' if gbs else '',
                gbs,
                class_='citation',
            ))
    if chunks:
        return HTML.span(*chunks)
    return ''


def language_identifier(req, obj, **kw):
    if not obj:
        return ''

    label = obj.name or obj.id

    for type_ in models.IdentifierType:
        if obj.type == type_.value:
            label = external_link(type_.args[0].format(obj), label=label, **kw)
            break

    return HTML.span(label, class_='language_identifier %s' % obj.type)


def get_referents(source, exclude=None):
    """Retrieve objects referencing source.

    :return: dict storing lists of objects referring to source keyed by type.
    """
    res = {}
    for obj_cls, ref_cls in [
        (models.Language, models.LanguageSource),
        (models.ValueSet, models.ValueSetReference),
        (models.Sentence, models.SentenceReference),
        (models.Contribution, models.ContributionReference),
    ]:
        if obj_cls.__name__.lower() in (exclude or []):
            continue
        q = DBSession.query(obj_cls).join(ref_cls).filter(ref_cls.source_pk == source.pk)
        if obj_cls == models.ValueSet:
            q = q.options(
                joinedload(models.ValueSet.parameter),
                joinedload(models.ValueSet.language))
        res[obj_cls.__name__.lower()] = q.all()
    return res


def alt_representations(req, rsc, doc_position='right', exclude=None):
    """Represent available adapters for rsc as dropdown menu."""
    kw = dict(doc_position=doc_position)
    if exclude:
        kw['exclude'] = exclude
    route, route_kw = req._route(rsc, None, ext='%s')
    dlw = DownloadWidget(
        req,
        rsc,
        rsc,
        JS_CLLD.route_url(route, route_kw),
        interfaces.IRepresentation,
        **kw)
    return dlw.render()


def partitioned(items, n=3):
    """Partition items into n buckets."""
    max_items_per_bucket, rem = divmod(len(items), n)
    if rem:
        max_items_per_bucket += 1
    bucket = []

    for item in items:
        if len(bucket) >= max_items_per_bucket:
            yield bucket
            bucket = []
        bucket.append(item)

    yield bucket


def marker_img(src, **kw):
    kw.setdefault('height', MARKER_IMG_DIM)
    kw.setdefault('width', MARKER_IMG_DIM)
    return HTML.img(src=src, **kw)


def icons(req, param):
    """Create an HTML snippet listing available icons.

    :param req: current request
    :param param: parameter name
    :return: HTML element
    """
    iconlist = req.registry.queryUtility(interfaces.IIconList)

    def td(icon):
        return HTML.td(
            marker_img(icon.url(req)),
            onclick='CLLD.reload({"%s": "%s"})' % (param, icon.name))
    rows = [
        HTML.tr(*map(td, icons)) for c, icons in
        groupby(sorted(iconlist, key=lambda i: i.name[1:]), lambda i: i.name[1:])]
    return HTML.div(
        HTML.table(
            HTML.tbody(*rows),
            class_="table table-condensed"
        ),
        button('Close', **{'data-dismiss': 'clickover'}))


def glottolog_url(glottocode):
    return models.Identifier(name=glottocode, type='glottolog').url()


def collapsed(id_, content, button_content=None):
    return HTML.div(
        HTML.p(HTML.a(
            button_content or icon('plus-sign'),
            **{'class': 'btn', 'data-toggle': 'collapse', 'data-target': '#%s' % id_})),
        HTML.div(content, id=id_, class_='collapse'))


def static_path(*comps):
    return os.path.abspath(
        os.path.join(os.path.dirname(clld.__file__), 'web', 'static', *comps))


def charis_font_spec_css():
    """Font spec for using CharisSIL with Pisa (xhtml2pdf)."""
    return """
    @font-face {{
        font-family: 'charissil';
        src: url('{0}/CharisSIL-R.ttf');
    }}
    @font-face {{
        font-family: 'charissil';
        font-style: italic;
        src: url('{0}/CharisSIL-I.ttf');
    }}
    @font-face {{
        font-family: 'charissil';
        font-weight: bold;
        src: url('{0}/CharisSIL-B.ttf');
    }}
    @font-face {{
        font-family: 'charissil';
        font-weight: bold;
        font-style: italic;
        src: url('{0}/CharisSIL-BI.ttf');
    }}
""".format(static_path('fonts'))


def get_resource_type(obj):
    """We rely on resource objects to implement just one interface.

    :param obj:
    :return: resource type as string
    """
    for interface in providedBy(obj):
        return interface.__name__[1:].lower()
