# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from sqlalchemy import Column, Integer, Unicode, ForeignKey

from clld.db.meta import DBSession, CustomModelMixin
from clld.db.models import common as cm
from clld.db.util import set_alembic_version
from clld.scripts.util import Data


class CustomLanguage(CustomModelMixin, cm.Language):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    custom = Column(Unicode)


class TestData(Data):
    def add_default(self, model, **kw):
        id_ = model.__name__.lower()
        kw.setdefault('id', id_)
        if hasattr(model, 'name') and not isinstance(model.name, property):
            kw.setdefault('name', model.__name__ + 'ä')
        if hasattr(model, 'description'):
            kw.setdefault('description', model.__name__ + 'ü')
        obj = self.add(model, id_, **kw)
        self[model] = obj
        return obj


def populate_test_db(engine):
    set_alembic_version(engine, '58559d4eea0d')

    data = TestData()
    data.add_default(
        cm.Dataset,
        domain='clld',
        jsondata={'license_icon': 'cc-by', 'license_url': 'http://example.org'})

    data.add_default(cm.Contributor, name='A Name', email='a@example.org')
    for id_, name in {
            'b': 'b Name',
            'c': 'c Name',
            'd': 'd Name'}.items():
        data.add(cm.Contributor, id_, id=id_, name=name, url='http://example.org')

    DBSession.add(
        cm.Editor(dataset=data[cm.Dataset], contributor=data[cm.Contributor]))

    data.add_default(cm.Source)
    data.add(
        cm.Source,
        'replaced',
        id='replaced',
        active=False,
        jsondata={'__replacement_id__': 'source'})

    data.add_default(cm.Contribution)
    cm.ContributionReference(contribution=data[cm.Contribution], source=data[cm.Source])

    for primary, c in [(True, 'contributor'), (False, 'b'), (True, 'c'), (False, 'd')]:
        cm.ContributionContributor(
            contribution=data[cm.Contribution],
            primary=primary,
            contributor=data['Contributor'][c])

    data.add_default(cm.Language, latitude=10.5, longitude=0.3)
    data[cm.Language].sources.append(data[cm.Source])

    for i, type_ in enumerate(cm.IdentifierType):
        cm.LanguageIdentifier(
            language=data[cm.Language],
            identifier=cm.Identifier(type=type_.value, id=type_.value + str(i), name='a'))

    cm.LanguageIdentifier(
        language=data[cm.Language],
        identifier=cm.Identifier(type='name', id='name', name='a'))

    for i in range(2, 102):
        _l = cm.Language(id='l%s' % i, name='Language %s' % i)
        _i = cm.Identifier(type='iso639-3', id='%.3i' % i, name='%.3i' % i)
        cm.LanguageIdentifier(language=_l, identifier=_i)
        DBSession.add(_l)

    param = data.add_default(cm.Parameter)
    de = cm.DomainElement(id='de', name='DomainElement', parameter=param)
    de2 = cm.DomainElement(id='de2', name='DomainElement2', parameter=param)

    valueset = data.add_default(
        cm.ValueSet,
        language=data[cm.Language],
        parameter=param,
        contribution=data[cm.Contribution])
    cm.ValueSetReference(valueset=valueset, source=data[cm.Source], description='10-20')

    data.add_default(
        cm.Value,
        domainelement=de,
        valueset=valueset,
        frequency=50,
        confidence='high')
    data.add(
        cm.Value, 'value2',
        id='value2',
        domainelement=de2,
        valueset=valueset,
        frequency=50,
        confidence='high')

    paramnd = data.add(
        cm.Parameter,
        'no-domain',
        id='no-domain',
        name='Parameter without domain')
    valueset = cm.ValueSet(
        id='vs2',
        language=data[cm.Language],
        parameter=paramnd,
        contribution=data[cm.Contribution])

    cm.ValueSetReference(valueset=valueset, source=data[cm.Source], description='10-20')
    cm.Value(id='v2', valueset=valueset, frequency=50, confidence='high')

    unit = data.add_default(cm.Unit, language=data[cm.Language])
    up = data.add_default(cm.UnitParameter)
    cm.UnitValue(
        id='unitvalue', name='UnitValue', unit=unit, unitparameter=up)

    up2 = cm.UnitParameter(id='up2', name='UnitParameter with domain')
    de = cm.UnitDomainElement(id='de', name='de', parameter=up2)
    DBSession.add(cm.UnitValue(
        id='uv2',
        name='UnitValue2',
        unit=unit,
        unitparameter=up2,
        unitdomainelement=de))

    DBSession.add(cm.Source(id='s'))

    sentence = data.add_default(
        cm.Sentence,
        description='sentence description',
        analyzed='a\tmorpheme\tdoes\tdo',
        gloss='a\tmorpheme\t1SG\tdo.SG2',
        source='own',
        comment='comment',
        original_script='a morpheme',
        language=data[cm.Language],
        jsondata={'alt_translation': 'Spanish: ...'})
    cm.SentenceReference(sentence=sentence, source=data[cm.Source])
    DBSession.add(cm.Config(key='key', value='value'))

    cm.Config.add_replacement('replaced', 'language', model=cm.Language)
    cm.Config.add_replacement('gone', None, model=cm.Language)
    DBSession.flush()
