# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

import pytest
from clld.db.models import common
from clld.web.datatables.unit import Units

from testutils import handle_dt


@pytest.mark.parametrize(
    "params",
    [
        {},
        {'language': 'language'},
    ])
def test_Units(request_factory, params):
    with request_factory(params=params) as req:
        handle_dt(req, Units, common.Unit)
