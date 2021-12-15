from clld.web import datatables
from clld.db.models.common import Language


def test_CsvAdapter(env):
    from clld.web.adapters.csv import CsvAdapter

    adapter = CsvAdapter(None)
    assert adapter.label
    res = adapter.render(
        datatables.Languages(env['request'], Language), env['request'])
    assert res.splitlines()
    assert adapter.render_to_response(
        datatables.Languages(env['request'], Language), env['request'])
