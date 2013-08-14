# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
import threading
from collections import namedtuple
import time
from wsgiref.simple_server import make_server, WSGIRequestHandler
import unittest
import re
from tempfile import mkdtemp
import warnings
warnings.filterwarnings(
    'ignore', message='At least one scoped session is already present.')

from mock import Mock, MagicMock
from path import path
from pyramid.paster import bootstrap
from pyramid.config import Configurator
import transaction
from sqlalchemy import create_engine
from webtest import TestApp
from webob.request import environ_add_POST
from zope.interface import Interface
try:
    from selenium import webdriver
    from selenium.webdriver.support.ui import Select
except ImportError:
    webdriver = None

import clld
from clld.db.meta import DBSession, VersionedDBSession, Base
from clld.db.models import common
from clld.web.adapters import Representation
from clld.web.icon import MapMarker
from clld import interfaces


ENV = None
TESTS_DIR = path(clld.__file__).dirname().joinpath('tests')


class Route(Mock):
    def __init__(self, name='home'):
        super(Mock, self).__init__()
        self.name = name


def main(global_config, **settings):
    """called when bootstrapping a pyramid app using clld/tests/test.ini
    """
    from clld.web.app import get_configurator

    class IF(Interface):
        """" """""

    settings['mako.directories'] = ['clld:web/templates']
    config = get_configurator(
        None, (MapMarker(), interfaces.IMapMarker), settings=settings)
    config.register_resource('testresource', common.Language, IF, with_index=True)
    config.register_resource('test2resource', Mock(), IF, with_index=False)
    config.register_adapter(Representation, Mock, name='test')
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
        language.sources.append(source)
        identifier = common.Identifier(type='iso639-3', id='iso')
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
    __cfg__ = TESTS_DIR.joinpath('test.ini').abspath()
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


def _add_header(headers, name, value):
    if isinstance(headers, dict):
        headers[name] = value
    else:
        headers.append((name, value))
    return headers


class ExtendedTestApp(TestApp):
    def get(self, *args, **kw):
        if kw.pop('xhr', False):
            kw['headers'] = _add_header(
                kw.pop('headers', {}), 'x-requested-with', str('XMLHttpRequest'))
        accept = kw.pop('accept', False)
        if accept:
            kw['headers'] = _add_header(
                kw.pop('headers', {}), 'accept', str(accept))
        return super(ExtendedTestApp, self).get(*args, **kw)


class TestWithApp(TestWithEnv):
    def setUp(self):
        TestWithEnv.setUp(self)
        self.app = ExtendedTestApp(self.env['app'])


class Handler(WSGIRequestHandler):  # pragma: no cover
    def log_message(self, *args, **kw):
        return


class ServerThread(threading.Thread):  # pragma: no cover
    """ Run WSGI server on a background thread.

    Pass in WSGI app object and serve pages from it for Selenium browser.
    """
    def __init__(self, app, host='0.0.0.0:8880'):
        threading.Thread.__init__(self)
        self.app = app
        self.host, self.port = host.split(':')
        self.srv = None

    def run(self):
        """
        Open WSGI server to listen to HOST_BASE address
        """
        self.srv = make_server(self.host, int(self.port), self.app, handler_class=Handler)
        try:
            self.srv.serve_forever()
        except:
            import traceback
            traceback.print_exc()
            # Failed to start
            self.srv = None

    def quit(self):
        """
        """
        if self.srv:
            self.srv.shutdown()


class PageObject(object):  # pragma: no cover
    """Virtual base class for objects we wish to interact with in selenium tests.
    """
    def __init__(self, browser, eid, url=None):
        """
        :param browser: The selenium webdriver instance.
        :param eid: Element id of a dom object.
        :param url: If specified, we first navigate to this url.
        """
        self.browser = browser
        if url:
            self.browser.get(url)
        self.eid = eid

    @property
    def e(self):
        try:
            return self.browser.find_element_by_id(self.eid)
        except:
            return self.browser.find_element_by_class_name(self.eid)


class Map(PageObject):  # pragma: no cover
    def __init__(self, browser, eid=None, url=None):
        super(Map, self).__init__(browser, eid or 'map-container', url=url)

    def test_show_marker(self, index=0):
        time.sleep(1)
        assert not self.e.find_elements_by_class_name('leaflet-popup-content')
        marker = self.e.find_elements_by_class_name('leaflet-marker-icon')
        marker[0].click()
        time.sleep(0.3)
        assert self.e.find_elements_by_class_name('leaflet-popup-content')

    def test_show_legend(self, name='iconsize'):
        e = self.e.find_element_by_id('legend-%s-container' % name)
        assert not e.is_displayed()
        opener = self.e.find_element_by_id('legend-%s-opener' % name)
        opener.click()
        time.sleep(0.3)
        assert e.is_displayed()
        opener.click()  # TODO: better test would be to click somewhere else!
        time.sleep(0.3)
        assert not e.is_displayed()


class DataTable(PageObject):  # pragma: no cover
    info_pattern = re.compile('\s+'.join([
        'Showing', '(?P<offset>[0-9,]+)',
        'to', '(?P<limit>[0-9,]+)',
        'of', '(?P<filtered>[0-9,]+)',
        'entries(\s*\(filtered from (?P<total>[0-9,]+) total entries\))?',
    ]))

    def __init__(self, browser, eid=None, url=None):
        time.sleep(0.5)
        super(DataTable, self).__init__(browser, eid or 'dataTables_wrapper', url=url)

    def get_info(self):
        """Parses the DataTables result info.
        """
        fieldnames = 'offset limit filtered total'
        res = []
        info = self.e.find_element_by_class_name('dataTables_info')
        m = self.info_pattern.search(info.text.strip())
        for n in fieldnames.split():
            n = m.group(n)
            if n:
                n = int(n.replace(',', ''))
            res.append(n)
        return namedtuple('Info', fieldnames)(*res)

    def get_first_row(self):
        """
        :return: list with text-values of the cells of the first table row.
        """
        table = None
        for t in self.e.find_elements_by_tag_name('table'):
            if 'dataTable' in t.get_attribute('class'):
                table = t
                break
        assert table
        tr = table.find_element_by_tag_name('tbody').find_element_by_tag_name('tr')
        return [td.text.strip() for td in tr.find_elements_by_tag_name('td')]

    def filter(self, name, value):
        """filters the table by using value for the column specified by name.

        Note that this abstracts the different ways filter controls can be implemented.
        """
        filter_ = self.e.find_element_by_id('dt-filter-%s' % name)
        if filter_.find_elements_by_tag_name('option'):
            filter_ = Select(filter_)
            filter_.select_by_visible_text(value)
        else:
            filter_.send_keys(value)
        time.sleep(2.5)

    def sort(self, label):
        """Triggers a table sort by clicking on the th Element specified by label.
        """
        sort = None
        for e in self.e.find_elements_by_xpath("//th[@class='sorting']"):
            if e.text.strip().startswith(label):
                sort = e
        assert sort
        sort.click()
        time.sleep(2.5)

    def download(self, fmt):
        opener = self.e.find_element_by_id('dt-dl-opener')
        link = self.e.find_element_by_id('dt-dl-%s' % fmt)
        assert not link.is_displayed()
        opener.click()
        assert link.is_displayed()
        link.click()


class TestWithSelenium(unittest.TestCase):  # pragma: no cover
    """run tests using selenium with the firefox driver
    """
    host = '0.0.0.0:8880'

    @classmethod
    def setUpClass(cls):
        """
        Create a Firefox test browser instance with hacked settings.

        We do this only once per testing module.
        """
        import logging
        selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        selenium_logger.setLevel(logging.WARNING)

        cls.downloads = path(mkdtemp())

        profile = webdriver.firefox.firefox_profile.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", str(cls.downloads))
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/x-bibtex")

        cls.browser = webdriver.Firefox(firefox_profile=profile)
        cls.server = ServerThread(cls.app, cls.host)
        cls.server.start()
        time.sleep(0.3)
        assert cls.server.srv

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        cls.server.quit()
        cls.downloads.rmtree()

    def url(self, path):
        assert path.startswith('/')
        return 'http://%s%s' % (self.host, path)

    def get_map(self, path, eid=None):
        return Map(self.browser, eid=eid, url=self.url(path))

    def get_datatable(self, path, eid=None):
        return DataTable(self.browser, eid=eid, url=self.url(path))
