import pytest

from clld.db.models import common
from clld.web.datatables.sentence import Sentences

from testutils import handle_dt


@pytest.mark.parametrize(
    "params",
    [
        {},
        {
            'sSearch_5': 'x',
            'sSearch_2': ' ',
            'iSortingCols': '1',
            'iSortCol_0': '5',
            'sSortDir_0': 'desc'},
        {
            'sSearch_4': 'text',
            'iSortingCols': '1',
            'iSortCol_0': '4',
            'sSortDir_0': 'desc'},
        {'parameter': 'parameter'},
        {'language': 'language'},
    ])
def test_plain(request_factory, params):
    with request_factory(params=params) as req:
        handle_dt(req, Sentences, common.Sentence)


def test_AudioCol(env, mocker):
    from clld.web.datatables.sentence import AudioCol, Sentences

    col = AudioCol(Sentences(env['request'], common.Sentence), 'audio')
    col.order()
    col.search('yes')
    col.format(mocker.Mock())
