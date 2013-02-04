from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession
from clld.db.models.common import Value, Parameter, DomainElement, Language, Contribution
from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol


class ValueNameCol(Col):

    def format(self, item):
        if item.domainelement:
            return item.domainelement.name
        return item.description

    def order(self):
        return DomainElement.id if self.dt.parameter.domain else Value.description

    def search(self, qs):
        if self.dt.parameter.domain:
            return DomainElement.name.contains(qs)
        return Value.description.contains(qs)


class LanguageCol(LinkCol):
    def get_obj(self, item):
        return item.language


class ParameterCol(LinkCol):
    def get_obj(self, item):
        return item.parameter


class _LinkToMapCol(LinkToMapCol):
    def get_obj(self, item):
        return item.language


class Values(DataTable):

    def __init__(self, req, model, parameter=None, contribution=None, search='col', **kw):
        self.search = search
        if parameter:
            self.parameter = parameter
        elif 'parameter' in req.params:
            self.parameter = DBSession.query(Parameter).get(int(req.params['parameter']))
        else:
            self.parameter = None

        if contribution:
            self.contribution = contribution
        elif 'contribution' in req.params:
            self.contribution = DBSession.query(Contribution).get(int(req.params['contribution']))
        else:
            self.contribution = None

        DataTable.__init__(self, req, model, **kw)

    def base_query(self, query):
        query = query.join(Language).join(Parameter).options(joinedload(Value.language))

        if self.parameter:
            query = query.outerjoin(DomainElement).options(joinedload(Value.domainelement))

        if self.parameter:
            return query.filter(Value.parameter_pk == self.parameter.pk)

        if self.contribution:
            return query.filter(Value.contribution_pk == self.contribution.pk)
        return query

    def col_defs(self):
        #
        # TODO: move the first col def to apics-specific table!
        #
        if self.contribution:
            res = [DetailsRowLinkCol(self)]
        else:
            res = []
        res.extend([
            LinkCol(self, 'id', get_label=lambda item: item.id, bSearchable=False),
            LanguageCol(self, 'language', model_col=Language.name),
        ])
        if self.parameter:
            res.extend([
                ValueNameCol(self, 'value', choices=[de.name for de in self.parameter.domain]),
                _LinkToMapCol(self)])
        else:
            res.extend([
                ParameterCol(self, 'parameter', model_col=Parameter.name),
                ValueNameCol(self, 'value')])
        return res

    def get_options(self):
        opts = DataTable.get_options(self)
        if self.parameter:
            opts['sAjaxSource'] = self.req.route_url('values', _query={'parameter': str(self.parameter.pk)})
            opts["aaSorting"] = [[2, "asc"]]
        if self.contribution:
            opts['sAjaxSource'] = self.req.route_url('values', _query={'contribution': str(self.contribution.pk)})
            opts["aaSorting"] = [[2, "asc"]]
        return opts
