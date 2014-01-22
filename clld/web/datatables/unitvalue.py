from sqlalchemy.orm import joinedload

from clld.db.models import common
from clld.web.datatables.base import DataTable, LinkCol


class UnitValueNameCol(LinkCol):
    def order(self):
        return common.UnitDomainElement.id \
            if self.dt.unitparameter and self.dt.unitparameter.domain \
            else [common.UnitValue.name, common.UnitValue.id]

    def search(self, qs):
        if self.dt.unitparameter and self.dt.unitparameter.domain:
            return common.UnitDomainElement.name.contains(qs)
        return common.UnitValue.name.contains(qs)


class Unitvalues(DataTable):
    __constraints__ = [common.UnitParameter, common.Contribution, common.Unit]

    def base_query(self, query):
        query = query\
            .join(common.Unit)\
            .outerjoin(common.UnitDomainElement)\
            .options(joinedload(common.UnitValue.unit))

        if self.unit:
            #query = query.join(common.UnitParameter, common.Contribution)
            return query.filter(common.UnitValue.unit_pk == self.unit.pk)

        if self.unitparameter:
            #query = query.join(common.Contribution, common.Unit)
            return query.filter(
                common.UnitValue.unitparameter_pk == self.unitparameter.pk)

        if self.contribution:
            #query = query.join(common.Unit, common.UnitParameter)
            return query.filter(common.UnitValue.contribution_pk == self.contribution.pk)

        return query

    def col_defs(self):
        name_col = UnitValueNameCol(self, 'value')
        if self.unitparameter and self.unitparameter.domain:
            name_col.choices = sorted([de.name for de in self.unitparameter.domain])
        return [
            name_col,
            LinkCol(self, 'unit', get_obj=lambda i: i.unit, model_col=common.Unit.name),
        ]

    def toolbar(self):
        return ''
