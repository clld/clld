from clld.db.models.common import Value
from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol
from clld.web.datatables.value import Values


class Parameters(DataTable):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
        ]
