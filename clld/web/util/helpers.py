from json import dumps
from itertools import groupby
import re

from sqlalchemy import or_
from markupsafe import Markup

from clld import interfaces
from clld import RESOURCES
from clld.web.util.htmllib import HTML, literal
from clld.db.meta import DBSession
from clld.db.models import common as models


class JS(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, *args):
        return '%s(%s)' % (self.name, ', '.join(
            arg.name if isinstance(arg, JS) else dumps(arg) for arg in args))

    def __getattr__(self, attr):
        return JS('%s.%s' % (self.name, attr))


JSFeed = JS('CLLD.Feed')
JSMap = JS('CLLD.Map')
JSModal = JS('CLLD.Modal')
JSDataTable = JS('CLLD.DataTable')


def format_frequency_and_confidence(value):
    res = ''
    if not (value.frequency or value.confidence):
        return res

    if value.frequency:
        res += 'Frequency: %s%%' % round(value.frequency, 1)

    if value.confidence:
        if res:
            res += ', '
        res += 'Confidence: %s' % value.confidence

    return ' (%s)' % res


def map_marker_img(req, obj, marker=None, height='20', width='20'):
    marker = marker or req.registry.queryUtility(interfaces.IMapMarker)
    if marker:
        url = marker(obj, req)
        if url:
            return HTML.img(src=url, height=height, width=width)
    return ''


def link(req, obj, **kw):
    rsc = None
    for _rsc in RESOURCES:
        if _rsc.interface.providedBy(obj):
            rsc = _rsc
            break

    assert rsc
    kw.setdefault('class', rsc.interface.__name__[1:])
    href = kw.pop('href', req.resource_url(obj, rsc=rsc, **kw.pop('url_kw', {})))
    label = kw.pop('label', getattr(obj, 'label', getattr(obj, 'name', obj.id)))
    kw.setdefault('title', label)
    return HTML.a(label, href=href, **kw)


def external_link(url, label=None):
    return HTML.a(icon('share'), ' ', label or url, href=url)


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
GLOSS_ABBR_PATTERN = re.compile('(?P<personprefix>1|2|3)?(?P<abbr>[A-Z]+)(?P<personsuffix>1|2|3)?(?=([^a-z]|$))')


def rendered_sentence(sentence, abbrs=None):
    assert sentence.xhtml or (sentence.analyzed and sentence.gloss)

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
                    explanation = '%s %s' % (person_map[match.group('personprefix')], explanation)

                if match.group('personsuffix'):
                    explanation = '%s %s' % (explanation, person_map[match.group('personsuffix')])

                res.append(HTML.span(
                    gloss[match.start():match.end()].lower(),
                    **{'data-original-title': explanation, 'rel': 'tooltip', 'class': 'sc ttip'}))
            else:
                res.append(abbr)

            end = match.end()

        res.append(gloss[end:])
        return filter(None, res)

    units = []
    for morpheme, gloss in zip(sentence.analyzed.split('\t'), sentence.gloss.split('\t')):
        units.append(HTML.div(
            HTML.div(morpheme, class_='morpheme'),
            HTML.div(*gloss_with_tooltip(gloss), **{'class': 'gloss'}),
            class_='gloss-unit'))

    return HTML.div(
        HTML.div(
            HTML.div(sentence.name, class_='object-language'),
            HTML.div(*units, **{'class': 'gloss-box'}),
            HTML.div(sentence.description, class_='translation') if sentence.description else '',
            HTML.div(sentence.original_script, class_='original_script') if sentence.original_script else '',
            HTML.blockquote(HTML.small(literal(sentence.comment)), class_='comment') if sentence.comment else '',
            class_='body',
        ),
        class_="sentence",
    )


def icon(class_, inverted=False):
    if not class_.startswith('icon-'):
        class_ = 'icon-' + class_
    if inverted:
        class_ = '%s icon-white' % class_
    return HTML.i(class_=class_)


def text2html(text):
    chunks = []
    for i, line in enumerate(text.split('\n')):
        if i > 0:
            chunks.append(HTML.br())
        chunks.append(line)
    return HTML.p(*chunks)


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
        if i > 0:
            chunks.append('; ')
        chunks.append(HTML.span(
            link(req, ref.source),
            HTML.span(
                ' [%s]' % ref.description if ref.description else '',
                class_='pages'),
            class_='citation',
        ))
    return HTML.span(*chunks)


def language_identifier(req, obj):
    label = obj.name or obj.id

    if obj.type == 'iso639-3':
        label = external_link('http://www.sil.org/iso639-3/documentation.asp?id=%s' % obj.id, label=label)
    elif obj.type == 'ethnologue':
        if re.match('[a-z]{3}', obj.id):
            label = external_link('http://www.ethnologue.com/language/%s' % obj.id, label=label)

    return HTML.span(label, class_='language_identifier %s' % obj.type)
