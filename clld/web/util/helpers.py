import re
from itertools import groupby  # we just import this to have it available in templates!
assert groupby  # appease pyflakes
import datetime  # we just import this to have it available in templates!
assert datetime
from urllib import urlencode

from six import PY3
if PY3:  # pragma: no cover
    from urllib.parse import quote
else:
    from urllib import quote

from sqlalchemy import or_
from markupsafe import Markup
from pyramid.renderers import render as pyramid_render
from pyramid.threadlocal import get_current_request

from clld import interfaces
from clld import RESOURCES
from clld.web.util.htmllib import HTML, literal
from clld.db.meta import DBSession
from clld.db.models import common as models
from clld.web.adapters import get_adapter
from clld.lib.coins import ContextObject
from clld.lib import bibtex
from clld.lib import rdf
from clld.util import xmlchars


def rdf_namespace_attrs():
    return '\n'.join('xmlns:%s="%s"' % item for item in rdf.NAMESPACES.items())


def urlescape(string):
    return quote(string, safe='')


def dumps(obj):
    return JS.sub(pyramid_render('json', obj))


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


def get_downloads(req):
    for k, items in groupby(
        sorted(
            list(req.registry.getUtilitiesFor(interfaces.IDownload)), key=lambda t: t[0]),
        lambda t: t[1].model.mapper_name() + 's',
    ):
        yield k, sorted([i[1] for i in items], key=lambda d: d.ext)


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


def format_frequency(req, obj, marker=None, height='20', width='20'):
    if not obj.frequency:
        return ''
    res = 'Frequency: %s%%' % round(obj.frequency, 1)
    marker = marker or req.registry.queryUtility(interfaces.IFrequencyMarker)
    if marker:
        url = marker(obj, req)
        if url:
            return HTML.img(src=url, height=height, width=width, alt=res, title=res)
    if not obj.frequency or obj.frequency == 100:
        return ''
    return res


def map_marker_img(req, obj, marker=None, height='20', width='20'):
    marker = marker or req.registry.getUtility(interfaces.IMapMarker)
    url = marker(obj, req)
    if url:
        return HTML.img(src=url, height=height, width=width)
    return ''


def link(req, obj, **kw):
    get_link_attrs = req.registry.queryUtility(interfaces.ILinkAttrs)
    if get_link_attrs:
        kw = get_link_attrs(req, obj, **kw)

    rsc = None
    rsc_name = kw.pop('rsc', None)
    for _rsc in RESOURCES:
        if _rsc.interface.providedBy(obj) or _rsc.name == rsc_name:
            rsc = _rsc
            break
    assert rsc
    href = kw.pop('href', req.resource_url(obj, rsc=rsc, **kw.pop('url_kw', {})))
    kw.setdefault('class', rsc.interface.__name__[1:])
    label = kw.pop('label', unicode(obj))
    kw.setdefault('title', label)
    return HTML.a(label, href=href, **kw)


def external_link(url, label=None, inverted=False, **kw):
    kw.setdefault('title', label or url)
    kw.setdefault('href', url)
    return HTML.a(icon('share', inverted=inverted), ' ', label or url, **kw)


def gbs_link(source, pages=None):
    if not source.google_book_search_id or not source.jsondata or not source.jsondata.get('gbs'):
        return ''
    if source.jsondata['gbs']['accessInfo']['viewability'] in ['NO_PAGES']:
        return ''
    pg = 'PP1'
    if pages:
        match = re.search('(?P<startpage>[0-9]+)', pages)
        if match:
            pg = 'PA' + match.group('startpage')
    return HTML.a(
        HTML.img(src="https://www.google.com/intl/en/googlebooks/images/gbs_preview_button1.gif"),
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


# regex to match standard abbreviations in gloss units:
# We look for sequences of uppercase letters which are not followed by a lowercase letter.
GLOSS_ABBR_PATTERN = re.compile(
    '(?P<personprefix>1|2|3)?(?P<abbr>[A-Z]+)(?P<personsuffix>1|2|3)?(?=([^a-z]|$))')


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
                res.append(literal(gloss[end:match.start()]))

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

        res.append(literal(gloss[end:]))
        return filter(None, res)

    units = []
    if sentence.analyzed and sentence.gloss:
        analyzed = sentence.analyzed
        glossed = sentence.gloss
        for morpheme, gloss in zip(analyzed.split('\t'), glossed.split('\t')):
            units.append(HTML.div(
                HTML.div(literal(morpheme), class_='morpheme'),
                HTML.div(*gloss_with_tooltip(gloss), **{'class': 'gloss'}),
                class_='gloss-unit'))

    return HTML.p(
        HTML.div(
            HTML.div(
                HTML.div(literal(sentence.markup_text or sentence.name), class_='object-language'),
                HTML.div(*units, **{'class': 'gloss-box'}) if units else '',
                HTML.div(sentence.description, class_='translation')
                if sentence.description else '',
                HTML.div(sentence.original_script, class_='original_script')
                if sentence.original_script else '',
                #HTML.small(literal(sentence.comment)) if sentence.comment and fmt == 'long' else '',
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
    chunks = []
    for i, line in enumerate(text.split('\n')):
        if i > 0:
            chunks.append(HTML.br())
        chunks.append(literal(line))
    return '\n'.join(chunks)


def text2html(text, mode='br', sep='\n\n'):
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
        if i == 0:
            chunks.append(' with ')
        if i > 0:
            chunks.append(' and ')
        chunks.append(link(req, c))

    return HTML.span(*chunks)


def linked_references(req, obj):
    chunks = []
    for i, ref in enumerate(getattr(obj, 'references', [])):
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
    return HTML.span(*chunks)


def language_identifier(req, obj):
    label = obj.name or obj.id

    if obj.type == 'iso639-3':
        label = external_link('http://www.sil.org/iso639-3/documentation.asp?id=%s'
                              % obj.id, label=label)
    elif obj.type == 'ethnologue':
        if re.match('[a-z]{3}', obj.id):
            label = external_link('http://www.ethnologue.com/language/%s'
                                  % obj.id, label=label)

    return HTML.span(label, class_='language_identifier %s' % obj.type)
