from sqlalchemy.orm import joinedload

from clld.db.models.common import Language, Sentence
from clld.web.datatables.base import (
    DataTable, LinkCol, DetailsRowLinkCol, LanguageCol, Col,
)


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
            LanguageCol(self, 'language'),
        ]
