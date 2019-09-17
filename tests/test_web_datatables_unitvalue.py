import pytest
from clld.db.models import common
from clld.web.datatables.unitvalue import Unitvalues

from testutils import handle_dt


@pytest.mark.parametrize(
    "params",
    [
        {},
        {
            'sSearch_0': '> 1',
            'sSearch_1': 's',
            'iSortingCols': '2',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc',
            'iSortCol_1': '1',
            'sSortDir_1': 'desc',
        },
        {'contribution': 'contribution'},
        {'unitparameter': 'unitparameter', 'sSearch_0': 's'},
        {'unitparameter': 'up2', 'sSearch_0': 's'},
        {'unit': 'unit'},
    ])
def test_Unitvalues(request_factory, params):
    with request_factory(params=params) as req:
        handle_dt(req, Unitvalues, common.UnitValue)
