from clld.db.models import common

from testutils import handle_dt


def test_Contributors(request_factory):
    from clld.web.datatables.contributor import Contributors

    with request_factory(params={
        'iSortingCols': '1',
        'iSortCol_0': '0',
        'sSortDir_0': 'desc'}
    ) as req:
        handle_dt(req, Contributors, common.Contributor)
