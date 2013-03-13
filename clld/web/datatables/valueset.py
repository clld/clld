from sqlalchemy.orm import joinedload, joinedload_all

from clld.db.models.common import (
    ValueSet, Parameter, Language, Contribution, ValueSetReference, Value,
)
from clld.web.datatables.base import (
    DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol, LanguageCol,
)
from clld.web.util.helpers import linked_references


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


class RefsCol(Col):
    def format(self, item):
        return linked_references(self.dt.req, item)


class Valuesets(DataTable):

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
        query = query.join(Language)\
            .options(
                joinedload(ValueSet.language),
                joinedload_all(ValueSet.references, ValueSetReference.source))

        if self.language:
            query = query.join(Parameter).options(joinedload(Value.parameter))
            return query.filter(Value.language_pk == self.language.pk)

        if self.parameter:
            return query.filter(Value.parameter_pk == self.parameter.pk)

        if self.contribution:
            query = query.join(Parameter)
            return query.filter(Value.contribution_pk == self.contribution.pk)

        return query

    def col_defs(self):
        #
        # TODO: move the first col def to apics-specific table!
        #
        #name_col = ValueNameCol(self, 'value')
        #if self.parameter and self.parameter.domain:
        #    name_col.choices = [de.name for de in self.parameter.domain]

        refs_col = RefsCol(self, 'references', bSearchable=False, bSortable=False)

        res = [DetailsRowLinkCol(self)]

        if self.parameter:
            return res + [
                LanguageCol(self, 'language', model_col=Language.name),
                #name_col,
                refs_col,
                _LinkToMapCol(self),
            ]

        if self.language:
            return res + [
                #name_col,
                ParameterCol(self, 'parameter', model_col=Parameter.name),
                refs_col,
                #
                # TODO: refs?
                #
            ]

        return res + [
            LanguageCol(self, 'language', model_col=Language.name),
            #name_col,
            ParameterCol(self, 'parameter', model_col=Parameter.name),
            refs_col,
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
                opts['sAjaxSource'] = self.req.route_url(
                    'values', _query={attr: getattr(self, attr).id})

        return opts
