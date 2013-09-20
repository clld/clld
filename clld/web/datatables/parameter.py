from clld.web.datatables.base import DataTable, LinkCol, DetailsRowLinkCol


class Parameters(DataTable):
    def col_defs(self):
        return [
            DetailsRowLinkCol(self, 'd'),
            LinkCol(self, 'name'),
        ]
