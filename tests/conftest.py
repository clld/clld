# coding: utf8
from __future__ import unicode_literals, print_function, division
import sys
import os

import pytest
from clldutils.path import Path
from sqlalchemy import Column, Unicode, Integer, ForeignKey
from clld.db.meta import CustomModelMixin, DBSession, VersionedDBSession
from clld.db.models import common
from clld.db.util import set_alembic_version
from clld.scripts.util import Data

if sys.version_info < (3, 5):  # pragma: no cover
    import pathlib2 as pathlib
else:
    import pathlib

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))


class CustomLanguage(CustomModelMixin, common.Language):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    custom = Column(Unicode)


@pytest.fixture
def custom_language():
    return CustomLanguage


@pytest.fixture
def testsdir():
    return Path(__file__).parent


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
        common.Dataset,
        domain='clld',
        jsondata={'license_icon': 'cc-by', 'license_url': 'http://example.org'})

    data.add_default(common.Contributor, name='A Name', email='a@example.org')
    for id_, name in {
        'b': 'b Name',
        'c': 'c Name',
        'd': 'd Name',
    }.items():
        data.add(common.Contributor, id_, id=id_, name=name, url='http://example.org')

    DBSession.add(
        common.Editor(dataset=data[common.Dataset], contributor=data[common.Contributor]))

    data.add_default(common.Source)
    data.add(
        common.Source,
        'replaced',
        id='replaced',
        active=False,
        jsondata={'__replacement_id__': 'source'})

    data.add_default(common.Contribution)
    common.ContributionReference(
        contribution=data[common.Contribution], source=data[common.Source])

    for primary, c in [(True, 'contributor'), (False, 'b'), (True, 'c'), (False, 'd')]:
        common.ContributionContributor(
            contribution=data[common.Contribution],
            primary=primary,
            contributor=data['Contributor'][c])

    data.add_default(common.Language, latitude=10.5, longitude=0.3)
    data[common.Language].sources.append(data[common.Source])

    for i, type_ in enumerate(common.IdentifierType):
        common.LanguageIdentifier(
            language=data[common.Language],
            identifier=common.Identifier(
                type=type_.value,
                id=type_.value + str(i),
                name='abc' if type_.name == 'iso' else 'glot1234'))

    common.LanguageIdentifier(
        language=data[common.Language],
        identifier=common.Identifier(type='name', id='name', name='a'))

    for i in range(2, 102):
        _l = common.Language(id='l%s' % i, name='Language %s' % i)
        _i = common.Identifier(type='iso639-3', id='%.3i' % i, name='abc')
        common.LanguageIdentifier(language=_l, identifier=_i)
        DBSession.add(_l)

    param = data.add_default(common.Parameter)
    de = common.DomainElement(id='de', name='DomainElement', parameter=param)
    de2 = common.DomainElement(id='de2', name='DomainElement2', parameter=param)

    valueset = data.add_default(
        common.ValueSet,
        language=data[common.Language],
        parameter=param,
        contribution=data[common.Contribution])
    common.ValueSetReference(
        valueset=valueset, source=data[common.Source], description='10-20')

    data.add_default(
        common.Value,
        domainelement=de,
        valueset=valueset,
        frequency=50,
        confidence='high')
    data.add(
        common.Value, 'value2',
        id='value2',
        domainelement=de2,
        valueset=valueset,
        frequency=50,
        confidence='high')

    paramnd = data.add(
        common.Parameter,
        'no-domain',
        id='no-domain',
        name='Parameter without domain')
    valueset = common.ValueSet(
        id='vs2',
        language=data[common.Language],
        parameter=paramnd,
        contribution=data[common.Contribution])

    common.ValueSetReference(
        valueset=valueset, source=data[common.Source], description='10-20')
    common.Value(id='v2', valueset=valueset, frequency=50, confidence='high')

    unit = data.add_default(common.Unit, language=data[common.Language])
    up = data.add_default(common.UnitParameter)
    common.UnitValue(
        id='unitvalue', name='UnitValue', unit=unit, unitparameter=up)

    up2 = common.UnitParameter(id='up2', name='UnitParameter with domain')
    de = common.UnitDomainElement(id='de', name='de', parameter=up2)
    DBSession.add(common.UnitValue(
        id='uv2',
        name='UnitValue2',
        unit=unit,
        unitparameter=up2,
        unitdomainelement=de))

    DBSession.add(common.Source(id='s'))

    sentence = data.add_default(
        common.Sentence,
        description='sentence description',
        analyzed='a\tmorpheme\tdoes\tdo',
        gloss='a\tmorpheme\t1SG\tdo.SG2',
        source='own',
        comment='comment',
        original_script='a morpheme',
        language=data[common.Language],
        jsondata={'alt_translation': 'Spanish: ...'})
    common.SentenceReference(sentence=sentence, source=data[common.Source])
    DBSession.add(common.Config(key='key', value='value'))

    common.Config.add_replacement('replaced', 'language', model=common.Language)
    common.Config.add_replacement('gone', None, model=common.Language)
    DBSession.flush()


@pytest.fixture
def db(db):
    try:
        yield db
    finally:
        DBSession.rollback()
        VersionedDBSession.rollback()


@pytest.fixture
def data(db):
    populate_test_db(db)
    yield db


@pytest.fixture()
def tmppath(tmpdir):
    return pathlib.Path(str(tmpdir))
