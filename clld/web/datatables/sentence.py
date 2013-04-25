from sqlalchemy.orm import joinedload

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


class Sentences(DataTable):
    def base_query(self, query):
        return query.join(Language).options(joinedload(Sentence.language))

    def col_defs(self):
        return [
            DetailsRowLinkCol(self),
            LinkCol(self, 'name'),
            Col(self, 'analyzed'),
            Col(self, 'gloss'),
            Col(self, 'description', sTitle=self.req.translate('Translation')),
            TypeCol(self),
            LanguageCol(self, 'language'),
        ]
