from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol


class Contributions(DataTable):

    def col_defs(self):
        return [
            LinkCol(self, 'name', route_name='contribution'),
        ]
