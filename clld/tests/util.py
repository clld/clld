from __future__ import unicode_literals
import unittest
import warnings
warnings.filterwarnings(
    'ignore', message='At least one scoped session is already present.')

from mock import Mock
from path import path
from pyramid.paster import bootstrap
from pyramid.config import Configurator
import transaction
from sqlalchemy import create_engine
from webtest import TestApp
from webob.request import environ_add_POST
from zope.interface import Interface

import clld
from clld.db.meta import DBSession, VersionedDBSession, Base
from clld.db.models import common
from clld.web.adapters import Representation
from clld.web.icon import MapMarker
from clld import interfaces


ENV = None


class Route(Mock):
    def __init__(self, name='home'):
        super(Mock, self).__init__()
        self.name = name


def main(global_config, **settings):
    class IF(Interface):
        """" """""

    settings['mako.directories'] = ['clld:web/templates']
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.register_app()
    config.registry.registerUtility(MapMarker(), interfaces.IMapMarker)
    config.register_resource('testresource', Mock(), IF, with_index=True)
    config.register_resource('test2resource', Mock(), IF, with_index=False)
    config.register_adapter(Representation, Mock, name='test')
    config.add_menu_item('test', lambda c, r: ('http://example.org', 'label'))
    return config.make_wsgi_app()


class TestWithDb(unittest.TestCase):
    def setUp(self):
        from clld.tests.fixtures import CustomLanguage

        assert CustomLanguage
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        VersionedDBSession.configure(bind=engine)
        Base.metadata.bind = engine
        Base.metadata.create_all()

    def tearDown(self):
        transaction.abort()


class TestWithDbAndData(TestWithDb):
    def setUp(self):
        TestWithDb.setUp(self)

        DBSession.add(common.Dataset(
            id='d', name='dataset', description='desc', domain='clld'))

        file_ = common.File(mime_type='text/plain', content='text')
        DBSession.add(file_)
        source = common.Source(id='src')
        contributors = {'a': 'A Name', 'b': 'b Name', 'c': 'c Name', 'd': 'd Name'}
        for id_, name in contributors.items():
            contributors[id_] = common.Contributor(id=id_, name=name)

        contribution = common.Contribution(id='c', name='Contribution')
        cr = common.ContributionReference(contribution=contribution, source=source)
        assert common.ContributionContributor(
            contribution=contribution, primary=True, contributor=contributors['a'])
        assert common.ContributionContributor(
            contribution=contribution, primary=False, contributor=contributors['b'])
        assert common.ContributionContributor(
            contribution=contribution, primary=True, contributor=contributors['c'])
        assert common.ContributionContributor(
            contribution=contribution, primary=False, contributor=contributors['d'])

        DBSession.add(contribution)

        language = common.Language(
            id='l1', name='Language 1', latitude=10.5, longitude=0.3)
        identifier = common.Identifier(type='iso639-3', id='iso')
        ls = common.LanguageSource(language=language, source=source)
        li = common.LanguageIdentifier(language=language, identifier=identifier)
        param = common.Parameter(id='p', name='Parameter')
        de = common.DomainElement(id='de', name='DomainElement', parameter=param)
        valueset = common.ValueSet(
            id='vs', language=language, parameter=param, contribution=contribution)
        value = common.Value(
            id='v',
            domainelement=de,
            valueset=valueset,
            frequency=50,
            confidence='high')
        DBSession.add(value)
        paramnd = common.Parameter(id='no-domain', name='Parameter without domain')
        valueset = common.ValueSet(
            id='vs2', language=language, parameter=paramnd, contribution=contribution)
        vr = common.ValueSetReference(valueset=valueset, source=source)
        value = common.Value(id='v2', valueset=valueset, frequency=50, confidence='high')
        DBSession.add(value)

        unit = common.Unit(id='u', name='Unit', language=language)
        up = common.UnitParameter(id='up', name='UnitParameter')
        DBSession.add(unit)
        DBSession.add(common.UnitValue(
            id='uv', name='UnitValue', unit=unit, unitparameter=up))

        up2 = common.UnitParameter(id='up2', name='UnitParameter with domain')
        de = common.UnitDomainElement(id='de', name='de', parameter=up2)
        DBSession.add(common.UnitValue(
            id='uv2',
            name='UnitValue2',
            unit=unit,
            unitparameter=up2,
            unitdomainelement=de))

        DBSession.add(common.Source(id='s'))

        sentence = common.Sentence(
            id='sentence',
            name='sentence name',
            description='sentence description',
            analyzed='a\tmorpheme\tdoes\tdo',
            gloss='a\tmorpheme\t1SG\tdo.SG2',
            source='own',
            comment='comment',
            original_script='a morpheme',
            language=language)
        sr = common.SentenceReference(sentence=sentence, source=source)
        DBSession.add(common.Config(key='key', value='value'))
        DBSession.flush()


class TestWithEnv(TestWithDbAndData):
    __cfg__ = path(clld.__file__).dirname().joinpath('tests', 'test.ini').abspath()
    __setup_db__ = True

    def setUp(self):
        if self.__setup_db__:
            TestWithDbAndData.setUp(self)

        global ENV

        if ENV is None:
            ENV = bootstrap(self.__cfg__)
            ENV['request'].translate = lambda s, **kw: s

        self.env = ENV
        self._prop_cache = {}

    def _set_request_property(self, k, v):
        if k == 'is_xhr':
            self.env['request'].environ['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'\
                if v else ''
        elif k == 'params':
            environ_add_POST(self.env['request'].environ, v)
        else:  # pragma: no cover
            try:
                setattr(self.env['request'], k, v)
            except:
                print(k)
                raise

    def set_request_properties(self, **props):
        for k, v in props.items():
            self._prop_cache[k] = getattr(self.env['request'], k, None)
            self._set_request_property(k, v)

    def handle_dt(self, cls, model, **kw):
        dt = cls(self.env['request'], model, **kw)
        dt.render()
        for item in dt.get_query():
            for col in dt.cols:
                col.format(item)
        return dt

    def tearDown(self):
        for k, v in self._prop_cache.items():
            self._set_request_property(k, v)
        self.env['request'].environ.pop('HTTP_X_REQUESTED_WITH', None)
        environ_add_POST(self.env['request'].environ, {})
        if self.__setup_db__:
            TestWithDbAndData.tearDown(self)


class TestWithApp(TestWithEnv):
    def setUp(self):
        TestWithEnv.setUp(self)
        self.app = TestApp(self.env['app'])
