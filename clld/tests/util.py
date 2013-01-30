from __future__ import unicode_literals
import unittest
import warnings
warnings.filterwarnings('ignore', message='At least one scoped session is already present.')

from path import path
from pyramid.paster import bootstrap
from pyramid.config import Configurator
import transaction
from sqlalchemy import create_engine, Column, Integer, Unicode, ForeignKey
from webtest import TestApp
from webob.request import environ_add_POST

import clld
from clld.db.meta import DBSession, VersionedDBSession, Base, CustomModelMixin
from clld.db.models import common


ENV = None


class CustomLanguage(common.Language, CustomModelMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    custom = Column(Unicode)


def main(global_config, **settings):
    settings['mako.directories'] = ['clld:web/templates']
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    return config.make_wsgi_app()


class TestWithDb(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://'#, echo=True
                               )
        DBSession.configure(bind=engine)
        VersionedDBSession.configure(bind=engine)
        Base.metadata.bind = engine
        Base.metadata.create_all()

    def tearDown(self):
        transaction.abort()


class TestWithDbAndData(TestWithDb):
    def setUp(self):
        TestWithDb.setUp(self)

        contributors = {'a': 'A Name', 'b': 'b Name'}
        for id_, name in contributors.items():
            contributors[id_] = common.Contributor(id=id_, name=name)

        contribution = common.Contribution(id='c', name='Contribution')
        assoc1 = common.ContributionContributor(
            contribution=contribution, primary=True, contributor=contributors['a'])
        assoc2 = common.ContributionContributor(
            contribution=contribution, primary=False, contributor=contributors['b'])
        DBSession.add(contribution)


class TestWithEnv(TestWithDbAndData):
    def setUp(self):
        TestWithDbAndData.setUp(self)
        global ENV

        if ENV is None:
            cfg = path(clld.__file__).dirname().joinpath('tests', 'test.ini').abspath()
            ENV = bootstrap(cfg)
            ENV['request'].translate = lambda s, **kw: s

        self.env = ENV
        self._prop_cache = {}

    def _set_request_property(self, k, v):
        if k == 'is_xhr':
            self.env['request'].environ['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest' if v else ''
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

    def tearDown(self):
        for k, v in self._prop_cache.items():
            self._set_request_property(k, v)
        TestWithDbAndData.tearDown(self)


class TestWithApp(TestWithEnv):
    def setUp(self):
        TestWithEnv.setUp(self)
        self.app = TestApp(self.env['app'])
