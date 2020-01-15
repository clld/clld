"""Default DataTable for ValueSet objects."""
import functools

from sqlalchemy.orm import joinedload

from clld.db.models.common import (
    ValueSet, Parameter, Language, Contribution, ValueSetReference,
)
from clld.web.datatables.base import (
    DataTable, LinkCol, DetailsRowLinkCol, LinkToMapCol, RefsCol,
)


class Valuesets(DataTable):

    """Default DataTable for ValueSet objects."""

    __constraints__ = [Parameter, Contribution, Language]

    def base_query(self, query):
        query = query.join(Language)\
            .options(
                joinedload(
                    ValueSet.language
                ),
                joinedload(
                    ValueSet.references
                ).joinedload(
                    ValueSetReference.source
                ))

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
        refs_col = RefsCol(self, 'references')
        res = [DetailsRowLinkCol(self, 'd')]

        def get(what, i):
            return getattr(i, {'p': 'parameter', 'l': 'language'}[what])

        if self.parameter:
            return res + [
                LinkCol(self, 'language',
                        model_col=Language.name, get_obj=functools.partial(get, 'l')),
                refs_col,
                LinkToMapCol(self, 'm', get_obj=functools.partial(get, 'l')),
            ]

        if self.language:
            return res + [
                LinkCol(self, 'parameter',
                        model_col=Parameter.name, get_obj=functools.partial(get, 'p')),
                refs_col,
            ]

        return res + [
            LinkCol(self, 'language', model_col=Language.name, get_obj=functools.partial(get, 'l')),
            LinkCol(
                self, 'parameter', model_col=Parameter.name, get_obj=functools.partial(get, 'p')),
            refs_col,
        ]

    def toolbar(self):
        return ''
