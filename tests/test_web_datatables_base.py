import pytest
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer
from zope.interface import Interface, classImplements

from clld.db.models import common
from clld.web.datatables.base import (
    DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol, IntegerIdCol, IdCol,
    ExternalLinkCol, filter_number, PercentCol,
)

from testutils import handle_dt


class Table(DataTable):
    __toolbar_kw__ = dict(exclude=['atom'])

    def col_defs(self):
        return [
            Col(self, 'pk'),
            DetailsRowLinkCol(self, 'd'),
            LinkToMapCol(self, 'm'),
            LinkCol(self, 'link'),
            Col(self, 'active'),
            Col(self, 'name', model_col=None, sDescription='MyName'),
            Col(self, 'description', format=lambda i: 'x'),
            IntegerIdCol(self, 'id'),
            IdCol(self, 'nid',
                  get_object=lambda i: i, model_col=common.Contributor.id),
            ExternalLinkCol(self, 'url'),
            Col(self, 'id', choices=['x', 'y'], select='multiple', sTooltip='xytt'),
        ]


def test_DataTable(env, request_factory):
    dt = Table(env['request'], common.Contributor)
    assert 'exclude' in dt._toolbar.options
    assert str(dt) == 'Contributors'
    assert repr(dt) == 'Contributors'
    dt.get_query(undefer_cols=['updated']).all()
    html = dt.render()
    assert 'xytt' in html
    assert ' multiple ' in html
    assert 'MyName' in html


@pytest.mark.parametrize('params', [
    {},
    {
        'sSearch_0': '1..1000000',
        'sSearch_4': 'True',
        'sSearch_6': 'e',
        'iSortingCols': '1',
        'iSortCol_0': '0',
        'sSortDir_0': 'desc',
    },
    {'iSortingCols': 'x'},
    {'iSortingCols': '1', 'iSortCol_0': '7'},
    {'sSearch_7': '1'},
    {'sSearch_8': 'id'},
    {'iDisplayLength': 'nonnumber'},
    {'iDisplayStart': 'nonnumber'},
])
def test_DataTable_cols(request_factory, params):
    with request_factory(params=params) as req:
        handle_dt(req, Table, common.Contributor)


def test_DataTable2(request_factory):
    class TestCol(Col):
        def search(self, qs):
            return filter_number(cast(self.dt.model.pk, Integer), qs, type_=int)

    class TestTable(DataTable):
        def col_defs(self):
            return [Col(self, 'latitude'), TestCol(self, 'pk')]

    with request_factory(params={'sSearch_0': '1..2,3..4'}) as req:
        handle_dt(req, TestTable, common.Language)

    with request_factory(params={'sSearch_0': '> 1', 'sSearch_1': '> 1'}) as req:
        handle_dt(req, TestTable, common.Language)


def test_DataTable3(env, request_factory):
    class TestTable(DataTable):
        def col_defs(self):
            return [PercentCol(self, 'frequency'), Col(self, 'name', choices=['a'])]

    handle_dt(env['request'], TestTable, common.Value)

    with request_factory(params={'sSearch_0': '> 10', 'sSearch_1': 'a'}) as req:
        handle_dt(req, TestTable, common.Value)


def test_DataTable_for_custom_class(env):
    from clld.web.datatables.base import DataTable

    class A(object):  # no route is registered for the name 'as' ...
        pass

    class ILanguage(Interface):  # but there is one for 'languages'!
        pass

    classImplements(A, ILanguage)
    dt = DataTable(env['request'], A)
    assert 'languages' in dt.options['sAjaxSource']
