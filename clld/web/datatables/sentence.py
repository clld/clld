from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer

from clld.db.meta import DBSession
from clld.db.util import get_distinct_values
from clld.db.models.common import (
    Language, Sentence, Parameter, ValueSentence, Value, ValueSet,
)
from clld.web.datatables.base import (
    DataTable, LinkCol, DetailsRowLinkCol, LanguageCol, Col,
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


class Sentences(DataTable):
    def __init__(self, req, model, parameter=None, language=None, **kw):
        for attr, _model in [('parameter', Parameter), ('language', Language)]:
            if locals()[attr]:
                setattr(self, attr, locals()[attr])
            elif attr in req.params:
                setattr(self, attr, _model.get(req.params[attr]))
            else:
                setattr(self, attr, None)

        DataTable.__init__(self, req, model, **kw)

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
            LinkCol(self, 'name', sTitle='Primary text', sClass="object-language"),
            Col(self, 'analyzed', sTitle='Analyzed text'),
            Col(self, 'gloss', sClass="gloss"),
            Col(self, 'description', sTitle=self.req.translate('Translation'), sClass="translation"),
            TypeCol(self, 'type'),
            LanguageCol(self, 'language'),
            DetailsRowLinkCol(self, 'd'),
        ]

    def get_options(self):
        return {'aaSorting': []}

    def xhr_query(self):
        for attr in ['parameter', 'language']:
            if getattr(self, attr):
                return {attr: getattr(self, attr).id}
