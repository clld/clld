import pytest
from clld.db.models import common
from clld.web.maps import (
    Map, ParameterMap, LanguageMap, SelectedLanguagesMap, CombinationMap, FilterLegend,
    Layer,
)


@pytest.mark.parametrize(
    "route,params,map_cls,ctx_cls,ctx_id",
    [
        ('language', dict(z=3, lat=1, lng=1), Map, common.Parameter, 'parameter'),
        ('language', {'z': 'abc'}, Map, common.Parameter, 'parameter'),
        ('parameter', {}, ParameterMap, common.Parameter, 'parameter'),
        ('parameter', {}, ParameterMap, common.Parameter, 'no-domain'),
        ('language', {}, LanguageMap, common.Language, 'language'),
    ])
def test_Map(request_factory, route, params, map_cls, ctx_cls, ctx_id):
    with request_factory(matched_route=route, params=params) as req:
        m = map_cls(ctx_cls.get(ctx_id), req)
        m.render()


def test_SelectedLanguagesMap(env):
    m = SelectedLanguagesMap(None, env['request'], [common.Language.first()])
    m.render()


def test_CombinationMap(env):
    ctx = common.Combination(common.Parameter.first())
    assert ctx.domain
    ctx.multiple = [common.Language.first()]
    dt = CombinationMap(ctx, env['request'])
    dt.render()


def test_layers(env):
    class TestMap(Map):
        def get_layers(self):
            yield Layer('l1', 'ln1', [], representation=555)
            yield Layer('l2', 'ln2', [], representation=333)

    m = TestMap(None, env['request'])
    assert '888' in m.render()


def test_FilterLegend(request_factory):
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

    with request_factory(matched_route='language') as req:
        map_ = FMap(common.Language.first(), req)
        map_.render()
