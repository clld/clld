from clld.db.models.common import Value
from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol
from clld.web.datatables.value import Values


class Sources(DataTable):
    def col_defs(self):
        return [
            DetailsRowLinkCol(self),
            LinkCol(self, 'name'),
            Col(self, 'description'),
            Col(self, 'year'),
            Col(self, 'authors'),
        ]
