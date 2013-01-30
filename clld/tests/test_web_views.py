from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotAcceptable

from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.interfaces import IDataTable


class Tests(TestWithEnv):
    def test_index_view(self):
        from clld.web.views import index_view

        ctx = self.env['registry'].getUtility(IDataTable, name='contributors')

        res = index_view(ctx(self.env['request'], common.Contributor), self.env['request'])
        self.assert_(isinstance(res, Response))

        self.set_request_properties(is_xhr=True, params={'sEcho': 'a'})
        res = index_view(ctx(self.env['request'], common.Contributor), self.env['request'])
        self.assertEquals(res.content_type, 'application/json')

        class X(ctx):
            def row_class(self, item):
                return 'row-%s' % item.pk

        res = index_view(X(self.env['request'], common.Contributor), self.env['request'])
        self.assertEquals(res.content_type, 'application/json')

    def test_resource_view(self):
        from clld.web.views import resource_view

        ctx = common.Language(id='a', name='Name')
        res = resource_view(ctx, self.env['request'])
        self.assert_(isinstance(res, Response))

        self.set_request_properties(matchdict={'ext': 'x'})
        self.assertRaises(HTTPNotAcceptable, resource_view, ctx, self.env['request'])

    def test__raise(self):
        from clld.web.views import _raise

        self.assertRaises(ValueError, _raise, None)

    def test__ping(self):
        from clld.web.views import _ping

        self.assertEquals(_ping(None)['status'], 'ok')
