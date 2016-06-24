# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def test_Unitvalues(self):
        from clld.web.datatables.unitvalue import Unitvalues

        dt = self.handle_dt(Unitvalues, common.UnitValue)
        self.assertTrue(isinstance(dt.options, dict))

        self.set_request_properties(params={
            'sSearch_0': '> 1',
            'sSearch_1': 's',
            'iSortingCols': '2',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc',
            'iSortCol_1': '1',
            'sSortDir_1': 'desc',
        })
        self.handle_dt(Unitvalues, common.UnitValue)

    def test_Unitvalues_with_contribution(self):
        from clld.web.datatables.unitvalue import Unitvalues

        contrib = common.Contribution.first()
        self.handle_dt(Unitvalues, common.UnitValue, contribution=contrib)
        self.set_request_properties(params=dict(contribution=contrib.id))
        self.handle_dt(Unitvalues, common.UnitValue)

    def test_Unitvalues_with_parameter(self):
        from clld.web.datatables.unitvalue import Unitvalues

        param = common.UnitParameter.first()
        self.handle_dt(Unitvalues, common.UnitValue, unitparameter=param)
        self.set_request_properties(params=dict(unitparameter=param.id, sSearch_0='s'))
        self.handle_dt(Unitvalues, common.UnitValue)
        self.set_request_properties(params=dict(unitparameter='up2', sSearch_0='s'))
        self.handle_dt(Unitvalues, common.UnitValue)

    def test_Unitvalues_with_unit(self):
        from clld.web.datatables.unitvalue import Unitvalues

        unit = common.Unit.first()
        self.handle_dt(Unitvalues, common.UnitValue, unit=unit)
        self.set_request_properties(params=dict(unit=unit.id))
        self.handle_dt(Unitvalues, common.UnitValue)
