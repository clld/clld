from functools import partial

from sqlalchemy.orm import joinedload, joinedload_all

from clld.db.models.common import (
    ValueSet, Parameter, Language, Contribution, ValueSetReference,
)
from clld.web.datatables.base import (
    DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol,
)
from clld.web.util.helpers import linked_references


class ParameterCol(LinkCol):
    def get_obj(self, item):
        return item.parameter


class _LinkToMapCol(LinkToMapCol):
    def get_obj(self, item):
        return item.language


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
            query = query.join(Parameter).options(joinedload(ValueSet.parameter))
            return query.filter(ValueSet.language_pk == self.language.pk)

        if self.parameter:
            return query.filter(ValueSet.parameter_pk == self.parameter.pk)

        if self.contribution:
            query = query.join(Parameter)
            return query.filter(ValueSet.contribution_pk == self.contribution.pk)

        return query

    def col_defs(self):
        refs_col = RefsCol(self, 'references', bSearchable=False, bSortable=False)
        res = [DetailsRowLinkCol(self, 'd')]
        get = lambda what, i: getattr(i, {'p': 'parameter', 'l': 'language'}[what])

        if self.parameter:
            return res + [
                LinkCol(self, 'language',
                        model_col=Language.name, get_obj=partial(get, 'l')),
                refs_col,
                LinkToMapCol(self, 'm', get_obj=partial(get, 'l')),
            ]

        if self.language:
            return res + [
                LinkCol(self, 'parameter',
                        model_col=Parameter.name, get_obj=partial(get, 'p')),
                refs_col,
            ]

        return res + [
            LinkCol(self, 'language', model_col=Language.name, get_obj=partial(get, 'l')),
            LinkCol(
                self, 'parameter', model_col=Parameter.name, get_obj=partial(get, 'p')),
            refs_col,
        ]

    def toolbar(self):
        return ''

    def xhr_query(self):
        for attr in ['parameter', 'contribution', 'language']:
            if getattr(self, attr):
                return {attr: getattr(self, attr).id}
