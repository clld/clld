from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession
from clld.db.models.common import Value, Parameter, DomainElement, Language, Contribution
from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol


class ValueNameCol(LinkCol):

    def get_attrs(self, item):
        label = item.domainelement.name if item.domainelement else (item.description or item.name or item.id)
        return {'label': label}

    def order(self):
        return DomainElement.id if self.dt.parameter and self.dt.parameter.domain else Value.description

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

    def get_layer(self, item):
        if item.domainelement:
            return item.domainelement.name
        return LinkToMapCol.get_layer(self, item)


class Values(DataTable):

    def __init__(self,
                 req,
                 model,
                 parameter=None,
                 contribution=None,
                 language=None,
                 search='col',
                 **kw):
        self.search = search

        for attr, _model in [
            ('parameter', Parameter),
            ('contribution', Contribution),
            ('language', Language),
        ]:
            if locals()[attr]:
                setattr(self, attr, locals()[attr])
            elif attr in req.params:
                setattr(self, attr, _model.get(req.params[attr]))
            else:
                setattr(self, attr, None)

        DataTable.__init__(self, req, model, **kw)

    def base_query(self, query):
        query = query.join(Language).options(joinedload(Value.language))

        if self.language:
            query = query.join(Parameter).options(joinedload(Value.parameter))
            return query.filter(Value.language_pk == self.language.pk)

        if self.parameter:
            query = query.outerjoin(DomainElement).options(joinedload(Value.domainelement))
            return query.filter(Value.parameter_pk == self.parameter.pk)

        if self.contribution:
            query = query.join(Parameter)
            return query.filter(Value.contribution_pk == self.contribution.pk)

        return query

    def col_defs(self):
        #
        # TODO: move the first col def to apics-specific table!
        #
        name_col = ValueNameCol(self, 'value')
        if self.parameter and self.parameter.domain:
            name_col.choices = [de.name for de in self.parameter.domain]

        if self.contribution:
            return [
                DetailsRowLinkCol(self),
                name_col,
                LanguageCol(self, 'language', model_col=Language.name),
                ParameterCol(self, 'parameter', model_col=Parameter.name),
            ]

        if self.parameter:
            return [
                name_col,
                LanguageCol(self, 'language', model_col=Language.name),
                _LinkToMapCol(self),
            ]

        if self.language:
            return [
                name_col,
                ParameterCol(self, 'parameter', model_col=Parameter.name),
                #
                # TODO: refs?
                #
            ]

        return [
            name_col,
            ParameterCol(self, 'parameter', model_col=Parameter.name),
            LanguageCol(self, 'language', model_col=Language.name),
            #
            # TODO: contribution col?
            #
        ]

    def toolbar(self):
        return ''

    def get_options(self):
        opts = DataTable.get_options(self)
        #opts["aaSorting"] = [[1, "asc"]]

        #opts['bLengthChange'] = False
        #opts['bPaginate'] = False
        #opts['bInfo'] = False

        for attr in ['parameter', 'contribution', 'language']:
            if getattr(self, attr):
                opts['sAjaxSource'] = self.req.route_url('values', _query={attr: getattr(self, attr).id})

        return opts
