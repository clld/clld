import pytest
from clld.db.models import common
from clld.web.datatables.valueset import Valuesets

from testutils import handle_dt


@pytest.mark.parametrize(
    "params",
    [
        {},
        {
            'sSearch_0': '> 1',
            'sSearch_1': 'x',
            'iSortingCols': '2',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc',
            'iSortCol_1': '1',
            'sSortDir_1': 'desc',
        },
        {'contribution': 'contribution'},
        {'language': 'language'},
        {'parameter': 'parameter'},
        {'parameter': 'no-domain'},
    ])
def test_Values(request_factory, params):
    with request_factory(params=params) as req:
        handle_dt(req, Valuesets, common.ValueSet)
