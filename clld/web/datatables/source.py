from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol


class Sources(DataTable):
    def col_defs(self):
        return [
            DetailsRowLinkCol(self),
            LinkCol(self, 'name'),
            Col(self, 'description'),
            Col(self, 'year'),
            Col(self, 'authors'),
        ]
