# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.db.models import common
from clld.web.datatables.unitparameter import Unitparameters

from testutils import handle_dt


def test_table(env):
    handle_dt(env['request'], Unitparameters, common.UnitParameter)
