import pytest
from clld.db.models import common
from clld.web.datatables.source import Sources

from testutils import handle_dt


@pytest.mark.parametrize(
    "params",
    [
        {},
        {
            'language': 'language',
            'sSearch_5': 'book',
            'iSortingCols': '1',
            'iSortCol_0': '5',
            'sSortDir_0': 'desc'},
    ])
def test_Sources(request_factory, params):
    with request_factory(params=params) as req:
        handle_dt(req, Sources, common.Source)
