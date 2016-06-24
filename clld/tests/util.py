# -*- coding: utf-8 -*-
"""Utilities to help with testing."""
from __future__ import absolute_import, division, unicode_literals
import threading
from collections import namedtuple
import time
from wsgiref.simple_server import make_server, WSGIRequestHandler
import unittest
import re
from tempfile import mkdtemp
from xml.etree import cElementTree as ElementTree
from json import loads
import warnings

from six import text_type
from mock import Mock
from pyramid.paster import bootstrap
from pyramid.config import Configurator
import transaction
from sqlalchemy import create_engine
from webtest import TestApp
from webob.request import environ_add_POST
from zope.interface import Interface
try:
    from selenium import webdriver
    from selenium.webdriver.support.ui import Select  # pragma: no cover
except ImportError:  # pragma: no cover
    webdriver = None
from clldutils.path import Path

import clld
from clld.db.meta import DBSession, VersionedDBSession, Base
from clld.web.adapters import Representation
from clld.web.icon import MapMarker
from clld import interfaces

warnings.filterwarnings(
    'ignore', message='At least one scoped session is already present.')

ENV = None
TESTS_DIR = Path(clld.__file__).parent.joinpath('tests')


class Route(Mock):

    """Mock a pyramid Route object."""

    def __init__(self, name='home'):
        super(Mock, self).__init__()
        self.name = name


def main(global_config, **settings):
    """called when bootstrapping a pyramid app using clld/tests/test.ini."""
    class IF(Interface):
        pass

    settings['mako.directories'] = ['clld:web/templates']
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.registry.registerUtility(MapMarker(), interfaces.IMapMarker)
    config.register_staticresource('css', 'clld:web/static/notexisting.css')
    config.register_staticresource('js', 'clld:web/static/notexisting.js')
    config.register_adapter(Representation, Mock, name='test')
    config.register_menu(('home', lambda ctx, req: (req.resource_url(req.dataset), 'tt')))
    return config.make_wsgi_app()


class WithCustomLanguageMixin(object):
    def setUp(self):
        from clld.tests.fixtures import CustomLanguage
        assert CustomLanguage

        super(WithCustomLanguageMixin, self).setUp()


def init_db():
    engine = create_engine('sqlite://')
    DBSession.configure(bind=engine)
    VersionedDBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all()
    return engine


class WithDbMixin(object):

    """For tests in need of a session bound to an empty db."""

    def setUp(self):
        super(WithDbMixin, self).setUp()
        init_db()

    def tearDown(self):
        transaction.abort()
        super(WithDbMixin, self).tearDown()


class WithDbAndDataMixin(object):

    """For tests in need of a session bound to a db with sample data."""

    def setUp(self):
        from clld.tests.fixtures import populate_test_db

        super(WithDbAndDataMixin, self).setUp()
        populate_test_db(init_db())

    def tearDown(self):
        transaction.abort()
        super(WithDbAndDataMixin, self).tearDown()


class TestWithEnv(unittest.TestCase):

    """For tests in need of a configured app."""

    __cfg__ = TESTS_DIR.joinpath('test.ini').resolve()

    def setUp(self):
        global ENV

        if ENV is None:
            ENV = bootstrap(self.__cfg__.as_posix())
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

    def utility(self, utility, interface):
        class Mgr(object):
            def __init__(self, registry, u, i):
                self.registry = registry
                self.utility = u
                self.provided = i

            def __enter__(self):
                self.registry.registerUtility(self.utility, self.provided)

            def __exit__(self, ext, exv, trb):
                self.registry.unregisterUtility(self.utility, self.provided)

        return Mgr(self.env['registry'], utility, interface)

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


def _add_header(headers, name, value):
    """Add (name, value) to headers.

    >>> headers = []
    >>> assert _add_header(headers, 'n', 'v') == [('n', 'v')]
    >>> headers = {}
    >>> assert _add_header(headers, 'n', 'v') == {'n': 'v'}
    """
    if isinstance(headers, dict):
        headers[name] = str(value)
    else:  # pragma: no cover
        headers.append((name, str(value)))
    return headers


class ExtendedTestApp(TestApp):

    """WebTest TestApp with extended support for evaluation of responses."""

    parsed_body = None

    def get(self, *args, **kw):
        if kw.pop('xhr', False):
            kw['headers'] = _add_header(
                kw.pop('headers', {}), 'x-requested-with', str('XMLHttpRequest'))
        accept = kw.pop('accept', False)
        if accept:
            kw['headers'] = _add_header(
                kw.pop('headers', {}), 'accept', str(accept))
        kw.setdefault('status', 200)
        body_parser = kw.pop('_parse_body', None)
        res = super(ExtendedTestApp, self).get(*args, **kw)
        if body_parser and res.status_int < 300:
            self.parsed_body = body_parser(res.body)
        return res

    def get_html(self, *args, **kw):
        from html5lib import parse

        docroot = kw.pop('docroot', None)
        res = self.get(*args, _parse_body=parse, **kw)
        child_nodes = list(self.parsed_body.getchildren())
        assert child_nodes
        if docroot:
            assert list(child_nodes[1].getchildren())[0].tag.endswith(docroot)
        return res

    def get_json(self, *args, **kw):
        _loads = lambda s: loads(text_type(s, encoding='utf8'))
        return self.get(*args, _parse_body=_loads, **kw)

    def get_xml(self, *args, **kw):
        return self.get(*args, _parse_body=ElementTree.fromstring, **kw)

    def get_dt(self, _path, *args, **kw):
        if 'sEcho=' not in _path:
            sep = '&' if '?' in _path else '?'
            _path = _path + sep + 'sEcho=1'
        kw.setdefault('xhr', True)
        return self.get_json(_path, *args, **kw)


class TestWithApp(TestWithEnv):

    """For tests in need of a running app."""

    def setUp(self):
        TestWithEnv.setUp(self)
        self.app = ExtendedTestApp(self.env['app'])


class Handler(WSGIRequestHandler):  # pragma: no cover

    """Logging HTTP request handler."""

    def log_message(self, *args, **kw):
        return


class ServerThread(threading.Thread):  # pragma: no cover

    """Run WSGI server on a background thread.

    Pass in WSGI app object and serve pages from it for Selenium browser.
    """

    def __init__(self, app, host='127.0.0.1:8880'):
        threading.Thread.__init__(self)
        self.app = app
        self.host, self.port = host.split(':')
        self.srv = None

    def run(self):
        """Open WSGI server to listen to HOST_BASE address."""
        self.srv = make_server(self.host, int(self.port), self.app, handler_class=Handler)
        try:
            self.srv.serve_forever()
        except:
            import traceback
            traceback.print_exc()
            # Failed to start
            self.srv = None

    def quit(self):
        if self.srv:
            self.srv.shutdown()


class PageObject(object):  # pragma: no cover

    """Virtual base class for objects we wish to interact with in selenium tests."""

    def __init__(self, browser, eid, url=None):
        """Initialize.

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

    """PageObject to interact with maps."""

    def __init__(self, browser, eid=None, url=None, sleep=2):
        super(Map, self).__init__(browser, eid or 'map-container', url=url)
        time.sleep(sleep)

    def test_show_marker(self, index=0):
        time.sleep(0.5)
        assert not self.e.find_elements_by_class_name('leaflet-popup-content')
        marker = self.e.find_elements_by_class_name('leaflet-marker-icon')
        marker[0].click()
        time.sleep(0.9)
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

    """PageObject to interact with DataTables."""

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
        """Parse the DataTables result info."""
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
        """Return a list with text-values of the cells of the first table row."""
        table = None
        for t in self.e.find_elements_by_tag_name('table'):
            if 'dataTable' in t.get_attribute('class'):
                table = t
                break
        assert table
        tr = table.find_element_by_tag_name('tbody').find_element_by_tag_name('tr')
        res = [td.text.strip() for td in tr.find_elements_by_tag_name('td')]
        return res

    def filter(self, name, value):
        """filter the table by using value for the column specified by name.

        Note that this abstracts the different ways filter controls can be implemented.
        """
        filter_ = self.e.find_element_by_id('dt-filter-%s' % name)
        if filter_.find_elements_by_tag_name('option'):
            filter_ = Select(filter_)
            filter_.select_by_visible_text(value)
        else:
            filter_.send_keys(value)
        time.sleep(2.5)

    def sort(self, label, sleep=2.5):
        """Trigger a table sort by clicking on the th Element specified by label."""
        sort = None
        for e in self.e.find_elements_by_xpath("//th"):
            if 'sorting' in e.get_attribute('class') and e.text.strip().startswith(label):
                sort = e
        assert sort
        sort.click()
        time.sleep(sleep)

    def download(self, fmt):
        opener = self.e.find_element_by_id('dt-dl-opener')
        link = self.e.find_element_by_id('dt-dl-%s' % fmt)
        assert not link.is_displayed()
        opener.click()
        assert link.is_displayed()
        link.click()


class TestWithSelenium(unittest.TestCase):  # pragma: no cover

    """run tests using selenium with the firefox driver."""

    host = '127.0.0.1:8880'

    @classmethod
    def setUpClass(cls):
        """
        Create a Firefox test browser instance with hacked settings.

        We do this only once per testing module.
        """
        import logging
        selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        selenium_logger.setLevel(logging.WARNING)

        cls.downloads = Path(mkdtemp())

        profile = webdriver.firefox.firefox_profile.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", cls.downloads.as_posix())
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

    def url(self, path):
        assert path.startswith('/')
        return 'http://%s%s' % (self.host, path)

    def get_map(self, path, eid=None, sleep=2):
        return Map(self.browser, eid=eid, url=self.url(path), sleep=sleep)

    def get_datatable(self, path, eid=None):
        return DataTable(self.browser, eid=eid, url=self.url(path))


class XmlResponse(object):

    """Wrapper for XML responses."""

    ns = None

    def __init__(self, response):
        self.raw = response.body
        self.root = ElementTree.fromstring(response.body)

    def findall(self, name):
        if not name.startswith('{') and self.ns:
            name = '{%s}%s' % (self.ns, name)
        return self.root.findall('.//%s' % name)

    def findone(self, name):
        _all = self.findall(name)
        if _all:
            return _all[0]
