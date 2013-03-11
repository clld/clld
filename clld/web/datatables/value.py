from sqlalchemy import desc
from sqlalchemy.orm import joinedload, joinedload_all, aliased

from clld.db.meta import DBSession
from clld.db.models.common import (
    Value, ValueSet, Parameter, DomainElement, Language, Contribution, ValueSetReference,
)
from clld.web.datatables.base import (
    DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol, LanguageCol,
)
from clld.web.util.helpers import linked_references, map_marker_img
from clld.web.util.htmllib import HTML, literal


class ValueNameCol(LinkCol):
    def get_obj(self, item):
        return item.valueset

    def get_attrs(self, item):
        label = item.domainelement.name if item.domainelement else (item.description or item.name or item.id)
        title = label
        if self.dt.parameter:
            label = HTML.span(map_marker_img(self.dt.req, item), literal('&nbsp;'), label)
        return {'label': label, 'title': title}

    def order(self):
        return DomainElement.id if self.dt.parameter and self.dt.parameter.domain else Value.description

    def search(self, qs):
        if self.dt.parameter and self.dt.parameter.domain:
            return DomainElement.name.contains(qs)
        return Value.description.contains(qs)


class ValueSetCol(LinkCol):
    def get_obj(self, item):
        return item.valueset

    def get_attrs(self, item):
        return {'label': item.valueset.name}


class ParameterCol(LinkCol):
    def get_obj(self, item):
        return item.valueset.parameter


class _LanguageCol(LanguageCol):
    def get_obj(self, item):
        return item.valueset.language


class _LinkToMapCol(LinkToMapCol):
    def get_obj(self, item):
        return item.valueset.language

    def get_layer(self, item):
        if item.domainelement:
            return item.domainelement.name
        return LinkToMapCol.get_layer(self, item.valueset)


class RefsCol(Col):
    def format(self, item):
        return linked_references(self.dt.req, item.valueset)


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
        query = query.join(ValueSet).options(
            joinedload_all(Value.valueset, ValueSet.references, ValueSetReference.source)
        )

        if self.language:
            query = query.join(ValueSet.parameter)
            return query.filter(ValueSet.language_pk == self.language.pk)

        if self.parameter:
            query = query.join(ValueSet.language)
            query = query.outerjoin(DomainElement).options(joinedload(Value.domainelement))
            return query.filter(ValueSet.parameter_pk == self.parameter.pk)

        if self.contribution:
            query = query.join(ValueSet.parameter)
            return query.filter(ValueSet.contribution_pk == self.contribution.pk)

        return query

    def col_defs(self):
        #
        # TODO: move the first col def to apics-specific table!
        #
        name_col = ValueNameCol(self, 'value')
        if self.parameter and self.parameter.domain:
            name_col.choices = [de.name for de in self.parameter.domain]

        refs_col = RefsCol(self, 'references', bSearchable=False, bSortable=False)

        res = [DetailsRowLinkCol(self)]

        if self.parameter:
            return res + [
                _LanguageCol(self, 'language', model_col=Language.name),
                name_col,
                refs_col,
                _LinkToMapCol(self),
            ]

        if self.language:
            return res + [
                name_col,
                ParameterCol(self, 'parameter', model_col=Parameter.name),
                refs_col,
                #
                # TODO: refs?
                #
            ]

        return res + [
            name_col,
            ValueSetCol(self, 'valueset', bSearchable=False, bSortable=False),
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
