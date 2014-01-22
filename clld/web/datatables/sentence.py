from sqlalchemy.orm import joinedload

from clld.db.util import get_distinct_values
from clld.db.models.common import (
    Language, Sentence, Parameter, ValueSentence, Value, ValueSet,
)
from clld.web.datatables.base import (
    DataTable, LinkCol, DetailsRowLinkCol, Col,
)


class TypeCol(Col):
    def __init__(self, dt, name, **kw):
        kw.setdefault('sTitle', dt.req.translate('Type'))
        kw.setdefault('choices', get_distinct_values(Sentence.type))
        super(TypeCol, self).__init__(dt, name, **kw)

    def search(self, qs):
        return Sentence.type == qs

    def format(self, item):
        return item.type

    def order(self):
        return Sentence.type


class TsvCol(Col):
    def search(self, qs):
        return super(TsvCol, self).search('\t'.join(qs.split()))


class Sentences(DataTable):
    __constraints__ = [Parameter, Language]

    def base_query(self, query):
        if self.language:
            query = query.filter(Sentence.language_pk == self.language.pk)
        else:
            query = query.join(Language).options(joinedload(Sentence.language))

        if self.parameter:
            query = query.join(ValueSentence, Value, ValueSet)\
                .filter(ValueSet.parameter_pk == self.parameter.pk)

        return query

    def col_defs(self):
        return [
            Col(self, 'id', bSortable=False, input_size='mini'),
            LinkCol(self, 'name', sTitle='Primary text', sClass="object-language"),
            TsvCol(self, 'analyzed', sTitle='Analyzed text'),
            TsvCol(self, 'gloss', sClass="gloss"),
            Col(self,
                'description',
                sTitle=self.req.translate('Translation'),
                sClass="translation"),
            TypeCol(self, 'type'),
            LinkCol(
                self,
                'language',
                model_col=Language.name,
                get_obj=lambda i: i.language,
                bSortable=not self.language,
                bSearchable=not self.language),
            DetailsRowLinkCol(self, 'd'),
        ]

    def get_options(self):
        return {'aaSorting': []}
