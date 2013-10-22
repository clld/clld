from sqlalchemy.orm import joinedload

from clld.db.models import common
from clld.web.datatables.base import DataTable, LinkCol
from clld.web.util.helpers import map_marker_img
from clld.web.util.htmllib import HTML, literal


class UnitValueNameCol(LinkCol):
    def order(self):
        return common.UnitDomainElement.id \
            if self.dt.parameter and self.dt.parameter.domain \
            else [common.UnitValue.name, common.UnitValue.id]

    def search(self, qs):
        if self.dt.parameter and self.dt.parameter.domain:
            return common.UnitDomainElement.name.contains(qs)
        return common.UnitValue.name.contains(qs)


class Unitvalues(DataTable):

    def __init__(self,
                 req,
                 model,
                 parameter=None,
                 contribution=None,
                 unit=None,
                 **kw):
        for attr, _model in [
            ('parameter', common.UnitParameter),
            ('contribution', common.Contribution),
            ('unit', common.Unit),
        ]:
            if locals()[attr]:
                setattr(self, attr, locals()[attr])
            elif attr in req.params:
                setattr(self, attr, _model.get(req.params[attr]))
            else:
                setattr(self, attr, None)

        DataTable.__init__(self, req, model, **kw)

    def base_query(self, query):
        query = query\
            .join(common.Unit)\
            .outerjoin(common.UnitDomainElement)\
            .options(joinedload(common.UnitValue.unit))

        if self.unit:
            #query = query.join(common.UnitParameter, common.Contribution)
            return query.filter(common.UnitValue.unit_pk == self.unit.pk)

        if self.parameter:
            #query = query.join(common.Contribution, common.Unit)
            return query.filter(common.UnitValue.unitparameter_pk == self.parameter.pk)

        if self.contribution:
            #query = query.join(common.Unit, common.UnitParameter)
            return query.filter(common.UnitValue.contribution_pk == self.contribution.pk)

        return query

    def col_defs(self):
        name_col = UnitValueNameCol(self, 'value')
        if self.parameter and self.parameter.domain:
            name_col.choices = sorted([de.name for de in self.parameter.domain])
        return [
            name_col,
            LinkCol(self, 'unit', get_obj=lambda i: i.unit, model_col=common.Unit.name),
        ]

    def toolbar(self):
        return ''

    def xhr_query(self):
        for attr in ['parameter', 'contribution', 'unit']:
            if getattr(self, attr):
                return {attr: getattr(self, attr).id}
