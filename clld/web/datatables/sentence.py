from sqlalchemy.orm import joinedload

from clld.db.models.common import Language, Sentence
from clld.web.datatables.base import (
    DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol, IdCol, LanguageCol,
)


class Sentences(DataTable):
    def base_query(self, query):
        return query.join(Language).options(joinedload(Sentence.language))

    def col_defs(self):
        return [
            DetailsRowLinkCol(self),
            LinkCol(self, 'name'),
            LanguageCol(self, 'language'),
        ]
