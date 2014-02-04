# coding: utf8
from __future__ import unicode_literals
import re
from itertools import groupby  # we just import this to have it available in templates!
assert groupby  # appease pyflakes
import datetime  # we just import this to have it available in templates!
assert datetime
from urllib import urlencode
from base64 import b64encode
from math import floor

from six import PY3
if PY3:  # pragma: no cover
    from urllib.parse import quote
else:
    from urllib import quote

try:
    import newrelic.agent
    assert newrelic.agent
    NEWRELIC = True
except ImportError:  # pragma: no cover
    NEWRELIC = False

from sqlalchemy import or_
from sqlalchemy.orm import joinedload_all
from markupsafe import Markup
from pyramid.renderers import render as pyramid_render
from pyramid.threadlocal import get_current_request
assert get_current_request
from pyramid.interfaces import IRoutesMapper

from clld import interfaces
from clld import RESOURCES
from clld.web.util.htmllib import HTML, literal
from clld.db.meta import DBSession
from clld.db.models import common as models
from clld.web.adapters import get_adapter, get_adapters
assert get_adapter
assert get_adapters
from clld.lib.coins import ContextObject
from clld.lib import bibtex
from clld.lib import rdf
from clld.util import xmlchars
assert xmlchars


def get_url_template(req, route, relative=True):
    if isinstance(route, basestring):
        route = req.registry.getUtility(IRoutesMapper).get_route(route)
    if route:
        res = '' if relative else req.application_url
        param_pattern = re.compile('\{(?P<name>[a-z]+)(:[^\}]+)?\}')
        return res + param_pattern.sub(lambda m: '{%s}' % m.group('name'), route.pattern)


def rdf_namespace_attrs():
    return '\n'.join('xmlns:%s="%s"' % item for item in rdf.NAMESPACES.items())


def urlescape(string):
    return quote(string, safe='')


def dumps(obj):
    return JS.sub(pyramid_render('json', obj))


def data_uri(filename, mimetype):
    with open(filename) as fp:
        content = fp.read()
    return 'data:%s;base64,%s' % (mimetype, b64encode(content))


class JS(object):
    delimiter = '|'
    pattern = re.compile('\"\{0}(?P<name>[^\{0}]+)\{0}\"'.format(delimiter))

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
        lambda t: t[1].model.mapper_name() + 's',
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
    """
    WGS84
    53° 33' 2" N, 9° 59' 36" E
    53.550556°, 9.993333°

    .. seealso:: http://en.wikipedia.org/wiki/ISO_6709#Order.2C_sign.2C_and_units
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
        return unicode(fmt).format(degrees, minutes, seconds)

    if not isinstance(obj.latitude, float) or not isinstance(obj.longitude, float):
        return ''
    return HTML.div(
        HTML.table(
            HTML.tr(
                HTML.td(
                    'Coordinates ',
                    external_link(
                        'http://en.wikipedia.org/wiki/World_Geodetic_System_1984',
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
    if 'license_icon' in req.dataset.jsondatadict:
        url = req.dataset.jsondatadict['license_icon']
        if not url.startswith('http'):
            url = req.static_url('clld:web/static/images/' + url)
        return url


def format_frequency(req, obj, marker=None, height='20', width='20'):
    if not obj.frequency or obj.frequency == 100:
        return ''
    res = 'Frequency: %s%%' % round(obj.frequency, 1)
    marker = marker or req.registry.queryUtility(interfaces.IFrequencyMarker)
    if marker:
        url = marker(obj, req)
        if url:
            return HTML.img(src=url, height=height, width=width, alt=res, title=res)
    return res


def map_marker_url(req, obj, marker=None):
    marker = marker or req.registry.getUtility(interfaces.IMapMarker)
    return marker(obj, req)


def map_marker_img(req, obj, marker=None, height='20', width='20'):
    url = map_marker_url(req, obj, marker=marker)
    if url:
        return HTML.img(src=url, height=height, width=width)
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
    label = kw.pop('label', unicode(obj))
    kw.setdefault('title', label)
    return HTML.a(label, href=href, **kw)


def external_link(url, label=None, inverted=False, **kw):
    kw.setdefault('title', label or url)
    kw.setdefault('href', url)
    return HTML.a(icon('share', inverted=inverted), ' ', label or url, **kw)


def link_to_map(language):
    return HTML.a(
        icon('icon-globe'),
        title='show %s on map' % language.name,
        href="#map",
        onclick=JS_CLLD.mapShowInfoWindow(None, language.id))


def gbs_link(source, pages=None):
    if not source or not source.google_book_search_id \
            or not source.jsondata or not source.jsondata.get('gbs'):
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
        href="http://books.google.com/books?id=%s&lpg=PP1&pg=%s" % (
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
ALT_TRANSLATION_LANGUAGE_PATTERN = re.compile('((?P<language>[a-zA-Z\s]+):)')


#
# TODO: enumerate exceptions: 1SG, 2SG, 3SG, ?PL, ?DU
#
def rendered_sentence(sentence, abbrs=None, fmt='long'):
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
        if sentence.jsondatadict.get('alt_translation'):
            text = sentence.jsondatadict['alt_translation']
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

    return HTML.p(
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
        class_="sentence",
    )


def icon(class_, inverted=False, **kw):
    if not class_.startswith('icon-'):
        class_ = 'icon-' + class_
    if inverted:
        class_ = '%s icon-white' % class_
    return HTML.i(class_=class_, **kw)


def contactmail(req, ctx=None, title='contact maintainer'):
    params = {}
    for name in ['subject', 'body']:
        params[name] = pyramid_render(
            'contactmail_{0}.mako'.format(name), {'req': req, 'ctx': ctx}, request=req)\
            .strip()\
            .encode('utf8')
    href = 'mailto:{0}?{1}'.format(req.dataset.contact, urlencode(params))
    return button(icon('bell'), title=title, href=href, class_='btn-warning btn-mini')


def newline2br(text):
    """
    >>> assert newline2br(None) == ''
    """
    if not text:
        return ''
    chunks = []
    for i, line in enumerate(text.split('\n')):
        if i > 0:
            chunks.append(HTML.br())
        chunks.append(literal(line))
    return '\n'.join(chunks)


def text2html(text, mode='br', sep='\n\n'):
    """
    >>> assert 'div' in unicode(text2html('chunk', mode='p'))
    """
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
    """
    :return: dict storing lists of objects referring to source keyed by type.
    """
    res = {}
    for obj_cls, ref_cls in [
        (models.Language, models.LanguageSource),
        (models.ValueSet, models.ValueSetReference),
        (models.Sentence, models.SentenceReference),
        (models.Contribution, models.ContributionReference),
    ]:
        if obj_cls.mapper_name().lower() in (exclude or []):
            continue
        q = DBSession.query(obj_cls).join(ref_cls).filter(ref_cls.source_pk == source.pk)
        if obj_cls == models.ValueSet:
            q = q.options(
                joinedload_all(models.ValueSet.parameter),
                joinedload_all(models.ValueSet.language))
        res[obj_cls.mapper_name().lower()] = q.all()
    return res


def alt_representations(req, rsc, doc_position='right', exclude=None):
    exclude = exclude or []
    exclude.extend(['html', 'snippet.html'])
    adapters = [a for n, a in req.registry.getAdapters([rsc], interfaces.IRepresentation)
                if a.extension not in set(exclude)]
    doc = []
    for adapter in adapters:
        if adapter.__doc__:
            doc.append(HTML.dt(adapter.name or adapter.extension))
            doc.append(HTML.dd(adapter.__doc__))
    doc = HTML.div(
        HTML.p(
            """You may download alternative representations of the data on
"%s" by clicking the button """ % rsc.name,
            icon('download-alt')),
        HTML.dl(*doc))
    return HTML.div(HTML.div(
        button(
            icon('info-sign', inverted=True),
            **{'class': ['btn-info'],
               'id': 'rsc-dl',
               'data-content': unicode(doc)}),
        HTML.a(
            icon('download-alt'),
            HTML.span(class_="caret"),
            **{
                'class_': "btn dropdown-toggle",
                'data-toggle': "dropdown",
                'href': "#",
                'id': "dt-dl-opener",
            }
        ),
        HTML.ul(
            *[HTML.li(HTML.a(
                a.name or a.extension,
                href="#",
                onclick="document.location.href = '%s'; return false;"
                        % req.resource_url(rsc, ext=a.extension),
                id='dt-dl-%s' % a.extension))
              for a in adapters],
            **dict(class_="dropdown-menu")),
        class_='btn-group'),
        HTML.script(literal("""\
    $(document).ready(function() {
        $('#rsc-dl').clickover({
            html: true,
            title: 'Alternative representations',
            placement: '%s',
            trigger: 'click'
        });
    });""" % doc_position)))


def partitioned(items, n=3):
    """
    >>> assert list(partitioned(range(10)))[0] == [0, 1, 2, 3]
    """
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
