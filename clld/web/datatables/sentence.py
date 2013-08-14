from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer

from clld.db.meta import DBSession
from clld.db.util import get_distinct_values
from clld.db.models.common import Language, Sentence
from clld.web.datatables.base import (
    DataTable, LinkCol, DetailsRowLinkCol, LanguageCol, Col,
)


class TypeCol(Col):
    def __init__(self, dt, name='type', **kw):
        kw.setdefault('sTitle', dt.req.translate('Type'))
        kw.setdefault('choices', get_distinct_values(Sentence.type))
        super(TypeCol, self).__init__(dt, name, **kw)

    def search(self, qs):
        return Sentence.type == qs

    def format(self, item):
        return item.type

    def order(self):
        return Sentence.type


class IdCol(Col):
    def __init__(self, dt, name='id', **kw):
        kw.setdefault('sTitle', dt.req.translate('No.'))
        kw.setdefault('sClass', 'right')
        kw.setdefault('input_size', 'mini')
        super(IdCol, self).__init__(dt, name, **kw)

    def order(self):
        return cast(self.dt.model.id, Integer)


class Sentences(DataTable):
    def base_query(self, query):
        return query.join(Language).options(joinedload(Sentence.language))

    def col_defs(self):
        return [
            #IdCol(self),
            LinkCol(self, 'name', sTitle='Primary text', sClass="object-language"),
            Col(self, 'analyzed', sTitle='Analyzed text'),
            Col(self, 'gloss', sClass="gloss"),
            Col(self, 'description', sTitle=self.req.translate('Translation'), sClass="translation"),
            TypeCol(self),
            LanguageCol(self, 'language'),
            DetailsRowLinkCol(self),
        ]

    def get_options(self):
        opts = super(Sentences, self).get_options()
        opts['aaSorting'] = []
        return opts
