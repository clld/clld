from sqlalchemy.orm import joinedload, joinedload_all

from clld.db.models.common import (
    Value, ValueSet, Parameter, DomainElement, Language, Contribution, ValueSetReference,
)
from clld.db.util import icontains
from clld.web.datatables.base import (
    DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol,
)
from clld.web.util.helpers import linked_references, map_marker_img
from clld.web.util.htmllib import HTML, literal


class ValueNameCol(LinkCol):
    def get_obj(self, item):
        return item.valueset

    def get_attrs(self, item):
        label = item.__unicode__()
        title = label
        if self.dt.parameter:
            label = HTML.span(map_marker_img(self.dt.req, item), literal('&nbsp;'), label)
        return {'label': label, 'title': title}

    def order(self):
        return DomainElement.number \
            if self.dt.parameter and self.dt.parameter.domain \
            else Value.description

    def search(self, qs):
        if self.dt.parameter and self.dt.parameter.domain:
            return DomainElement.name.__eq__(qs)
        return icontains(Value.description, qs)


class ValueSetCol(LinkCol):
    def get_obj(self, item):
        return item.valueset

    def get_attrs(self, item):
        return {'label': item.valueset.name}


class RefsCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        return ', '.join(filter(
            None, [item.valueset.source, linked_references(self.dt.req, item.valueset)]))


class Values(DataTable):
    __constraints__ = [Parameter, Contribution, Language]

    def base_query(self, query):
        query = query.join(ValueSet).options(
            joinedload_all(Value.valueset, ValueSet.references, ValueSetReference.source)
        )

        if self.language:
            query = query.join(ValueSet.parameter)
            return query.filter(ValueSet.language_pk == self.language.pk)

        if self.parameter:
            query = query.join(ValueSet.language)
            query = query.outerjoin(DomainElement).options(
                joinedload(Value.domainelement))
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

        res = [DetailsRowLinkCol(self, 'd')]

        if self.parameter:
            return res + [
                LinkCol(self,
                        'language',
                        model_col=Language.name,
                        get_object=lambda i: i.valueset.language),
                name_col,
                RefsCol(self, 'source'),
                LinkToMapCol(self, 'm', get_object=lambda i: i.valueset.language),
            ]

        if self.language:
            return res + [
                name_col,
                LinkCol(self,
                        'parameter',
                        sTitle=self.req.translate('Parameter'),
                        model_col=Parameter.name,
                        get_object=lambda i: i.valueset.parameter),
                RefsCol(self, 'source'),
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
