from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession
from clld.db.models.common import Value, Parameter, DomainElement, Language
from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol


class ValueNameCol(Col):

    def format(self, item):
        if item.domainelement:
            return item.domainelement.name
        return item.description

    def order(self, direction):
        order_col = DomainElement.id if self.dt.parameter.domain else Value.description
        return desc(order_col) if direction == 'desc' else order_col

    def search(self, qs):
        if self.dt.parameter.domain:
            return DomainElement.name.contains(qs)
        return Value.description.contains(qs)


class Values(DataTable):

    def __init__(self, req, model, parameter=None, search='col', **kw):
        self.search = search
        if parameter:
            self.parameter = parameter
        elif 'parameter' in req.params:
            self.parameter = DBSession.query(Parameter).get(int(req.params['parameter']))

        DataTable.__init__(self, req, model, **kw)

    def base_query(self, query):
        query = query.join(Language).options(joinedload(Value.language))

        if self.parameter:
            query = query.outerjoin(DomainElement).options(joinedload(Value.domainelement))

        if self.parameter:
            return query.filter(Value.parameter_pk == self.parameter.pk)
        return query

    def col_defs(self):
        return [
            LinkCol(self, 'id', route_name='value', get_label=lambda item: item.id, bSearchable=False),
            LinkCol(self, 'language', route_name='language', get_label=lambda item: item.language.name, model_col=Language.name),
            ValueNameCol(self, 'value', choices=[de.name for de in self.parameter.domain]),
        ]

    def get_options(self):
        opts = DataTable.get_options(self)
        if self.parameter:
            opts['sAjaxSource'] = self.req.route_url('values', _query={'parameter': str(self.parameter.pk)})
            opts["aaSorting"] = [[ 2, "asc" ]]
        return opts
