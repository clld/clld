# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.tests.util import TestWithEnv, WithDbAndDataMixin, Route
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def set_route(self, name='language'):
        self.set_request_properties(matched_route=Route(name))

    def test_Map(self):
        from clld.web.maps import Map

        self.set_route()
        self.set_request_properties(params=dict(z=3, lat=1, lng=1))

        dt = Map(common.Parameter.first(), self.env['request'])
        dt.render()

        self.set_request_properties(params=dict(z='abc'))
        dt = Map(common.Parameter.first(), self.env['request'])
        dt.render()

    def test_ParameterMap(self):
        from clld.web.maps import ParameterMap

        self.set_route('parameter')

        dt = ParameterMap(common.Parameter.get('parameter'), self.env['request'])
        for l in dt.layers:
            l.representation = 5
        dt.render()

        dt = ParameterMap(common.Parameter.get('no-domain'), self.env['request'])
        dt.render()

    def test_LanguageMap(self):
        from clld.web.maps import LanguageMap

        self.set_route()
        dt = LanguageMap(common.Language.first(), self.env['request'])
        dt.render()

    def test_SelectedLanguagesMap(self):
        from clld.web.maps import SelectedLanguagesMap

        m = SelectedLanguagesMap(None, self.env['request'], [common.Language.first()])
        m.render()

    def test_CombinationMap(self):
        from clld.web.maps import CombinationMap

        ctx = common.Combination(common.Parameter.first())
        assert ctx.domain
        ctx.multiple = [common.Language.first()]
        dt = CombinationMap(ctx, self.env['request'])
        dt.render()

    def test_FilterLegend(self):
        from clld.web.maps import FilterLegend, Map
        from clld.web.datatables import Languages

        class FLanguages(Languages):
            def col_defs(self):
                cols = Languages.col_defs(self)
                cols[1].choices = ['name']
                return cols

        class FMap(Map):
            def get_legends(self):
                yield FilterLegend(
                    self,
                    '',
                    col='name',
                    dt=FLanguages(self.req, common.Language))

        self.set_route()
        map_ = FMap(common.Language.first(), self.env['request'])
        map_.render()
