from __future__ import unicode_literals

from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotAcceptable, HTTPNotFound, HTTPGone, HTTPFound
from mock import Mock, patch
from requests.exceptions import ReadTimeout

from clld.tests.util import TestWithEnv, XmlResponse, WithDbAndDataMixin
from clld.db.models import common
from clld.interfaces import IDataTable


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_index_view(self):
        from clld.web.views import index_view

        ctx = self.env['registry'].getUtility(IDataTable, name='contributors')

        # note: this invocation of the index view does also exercise the ExcelAdapter
        res = index_view(
            ctx(self.env['request'], common.Contributor), self.env['request'])
        self.assertTrue(isinstance(res, Response))
        res = index_view(
            ctx(self.env['request'], common.Sentence), self.env['request'])
        res = index_view(
            ctx(self.env['request'], common.Value), self.env['request'])

        self.set_request_properties(is_xhr=True, params={'sEcho': 'a'})
        res = index_view(
            ctx(self.env['request'], common.Contributor), self.env['request'])
        self.assertEqual(res.content_type, 'application/json')

        class X(ctx):
            def row_class(self, item):
                return 'row-%s' % item.pk

        res = index_view(X(self.env['request'], common.Contributor), self.env['request'])
        self.assertEqual(res.content_type, 'application/json')

        class Route(Mock):
            name = 'contributors_alt'

        self.set_request_properties(
            is_xhr=False, matched_route=Route(), matchdict={'ext': 'csv'})
        index_view(ctx(self.env['request'], common.Contributor), self.env['request'])

    def test_resource_view(self):
        from clld.web.views import resource_view

        ctx = common.Language(id='a', name='Name')
        res = resource_view(ctx, self.env['request'])
        self.assertTrue(isinstance(res, Response))

        self.set_request_properties(matchdict={'ext': 'x'})
        self.assertRaises(HTTPNotAcceptable, resource_view, ctx, self.env['request'])

    def test_select_combination(self):
        from clld.web.views import select_combination

        self.assertRaises(HTTPNotFound, select_combination, None, self.env['request'])
        self.set_request_properties(
            params={'parameters': 'parameter'})
        self.assertRaises(HTTPFound, select_combination, None, self.env['request'])
        self.set_request_properties(
            params=[('parameters', 'parameter'), ('parameters', 'no-domain')])
        self.assertRaises(HTTPFound, select_combination, None, self.env['request'])

    def test__raise(self):
        from clld.web.views import _raise

        self.assertRaises(ValueError, _raise, None)

    def test__ping(self):
        from clld.web.views import _ping

        self.assertEqual(_ping(None)['status'], 'ok')

    def test_js(self):
        from clld.web.views import js

        js(self.env['request'])

    def test_gone(self):
        from clld.web.views import gone

        self.assertRaises(HTTPGone, gone, None, None)

    def test_redirect(self):
        from clld.web.views import redirect

        self.assertRaises(HTTPFound, redirect, HTTPFound, lambda r: 'x', None, None)

    def test_unapi(self):
        from clld.web.views import unapi

        assert XmlResponse(unapi(self.env['request'])).root.tag == 'formats'

        self.set_request_properties(params={'format': 'bib'})
        self.assertTrue(isinstance(unapi(self.env['request']), HTTPNotFound))

        self.set_request_properties(params={'id': '/contributions/ccc'})
        self.assertTrue(isinstance(unapi(self.env['request']), HTTPNotFound))

        self.set_request_properties(params={'id': '/contributions/contribution'})
        assert XmlResponse(unapi(self.env['request'])).findall('format')

        self.set_request_properties(params={'format': 'bib', 'id': '/languages/language'})
        unapi(self.env['request'])
        self.set_request_properties(
            params={'format': 'bibtex', 'id': '/contributions/contribution'})
        unapi(self.env['request'])

    def test_atom_feed(self):
        from clld.web.views import atom_feed

        class FeedResponseWithTitle(object):
            status_code = 200
            content = b"""\
<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"
      xmlns:dc="http://purl.org/dc/elements/1.1/"
      xmlns:atom="http://www.w3.org/2005/Atom"
      xmlns:sy="http://purl.org/rss/1.0/modules/syndication/">
<channel>
    <title>Comments for The World Atlas of Language Structures Online</title>
    <link>http://blog.wals.info</link>
    <description>WALS Online Blog</description>
        <item>
        <title>Comment on Datapoint</title>
        <link>http://blog.wals.info/datapoint</link>
        <pubDate>Wed, 04 Nov 2015 22:11:03 +0000</pubDate>
        <guid>http://blog.wals.info/datapoint-26a-wals_code_juk/</guid>
        <description>Some description</description>
        <content:encoded><![CDATA[<p>some description</p>
]]></content:encoded>
    </item>
</channel>
"""

        class FeedResponseWithoutTitle(object):
            status_code = 200
            content = b"""\
<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"
      xmlns:dc="http://purl.org/dc/elements/1.1/"
      xmlns:atom="http://www.w3.org/2005/Atom"
      xmlns:sy="http://purl.org/rss/1.0/modules/syndication/">
<channel>
    <link>http://blog.wals.info</link>
    <description>WALS Online Blog</description>
</channel>
"""

        class MockRequests1(object):
            get = Mock(return_value=FeedResponseWithTitle)

        class MockRequests2(object):
            get = Mock(return_value=FeedResponseWithoutTitle)

        class MockRequestsTimeout(object):
            def get(self, *args, **kw):
                raise ReadTimeout()

        with patch('clld.web.views.requests', MockRequests1()):
            res = atom_feed(self.env['request'], None)
            self.assertIn('<entry>', res.body.decode('utf8'))

        with patch('clld.web.views.requests', MockRequests2()):
            res = atom_feed(self.env['request'], None)
            self.assertNotIn('<entry>', res.body.decode('utf8'))

        with patch('clld.web.views.requests', MockRequestsTimeout()):
            res = atom_feed(self.env['request'], None)
            self.assertNotIn('<entry>', res.body.decode('utf8'))
