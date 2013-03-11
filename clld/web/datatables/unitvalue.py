from sqlalchemy import desc
from sqlalchemy.orm import joinedload, joinedload_all, aliased

from clld.db.meta import DBSession
from clld.db.models import common
from clld.web.datatables.base import (
    DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol, LanguageCol,
)
from clld.web.util.helpers import linked_references, map_marker_img
from clld.web.util.htmllib import HTML, literal


class UnitValueNameCol(LinkCol):
    def get_attrs(self, item):
        label = item.unitdomainelement.name if item.unitdomainelement else (item.name or item.id)
        title = label
        if self.dt.parameter:
            label = HTML.span(map_marker_img(self.dt.req, item), literal('&nbsp;'), label)
        return {'label': label, 'title': title}

    def order(self):
        return common.UnitDomainElement.id if self.dt.parameter and self.dt.parameter.domain \
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
        query = query.outerjoin(common.UnitDomainElement)

        if self.unit:
            query = query.join(common.UnitParameter, common.Contribution)
            return query.filter(common.UnitValue.unit_pk == self.unit.pk)

        if self.parameter:
            query = query.join(common.Contribution, common.Unit)
            return query.filter(common.UnitValue.unitparameter_pk == self.parameter.pk)

        if self.contribution:
            query = query.join(common.Unit, common.UnitParameter)
            return query.filter(common.UnitValue.contribution_pk == self.contribution.pk)

        return query

    def col_defs(self):
        name_col = UnitValueNameCol(self, 'value')
        if self.parameter and self.parameter.domain:
            name_col.choices = sorted([de.name for de in self.parameter.domain])
        return [name_col]

    def toolbar(self):
        return ''

    def get_options(self):
        opts = DataTable.get_options(self)
        for attr in ['parameter', 'contribution', 'unit']:
            if getattr(self, attr):
                opts['sAjaxSource'] = self.req.route_url('unitvalues', _query={attr: getattr(self, attr).id})

        return opts
