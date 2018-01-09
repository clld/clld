from __future__ import unicode_literals, division, absolute_import, print_function
import json

from clld.web import datatables
from clld.db.models.common import Language, ValueSet


def test_CsvAdapter(env):
    from clld.web.adapters.csv import CsvAdapter

    adapter = CsvAdapter(None)
    assert adapter.label
    res = adapter.render(
        datatables.Languages(env['request'], Language), env['request'])
    assert res.splitlines()
    assert adapter.render_to_response(
        datatables.Languages(env['request'], Language), env['request'])


def test_CsvwJsonAdapter(request_factory, env):
    from clld.web.adapters.csv import CsvmJsonAdapter

    adapter = CsvmJsonAdapter(None)
    res = json.loads(adapter.render(
        datatables.Languages(env['request'], Language), env['request']))
    assert res['tableSchema']['columns'] != []

    res = adapter.render(
        datatables.Valuesets(env['request'], ValueSet), env['request'])
    assert 'foreignKeys' in json.loads(res)['tableSchema']
    adapter.render_to_response(
        datatables.Valuesets(env['request'], ValueSet), env['request'])

    with request_factory(params={'sSearch_0': 'xyz'}) as req:
        res = json.loads(adapter.render(datatables.Languages(req, Language), req))
        assert res['tableSchema']['columns'] == []
