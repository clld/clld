from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol


class Languages(DataTable):
    def col_defs(self):
        return [
            DetailsRowLinkCol(self, route_name='language'),
            LinkCol(self, 'id', route_name='language', get_label=lambda item: item.id),
            LinkCol(self, 'name', route_name='language'),
            LinkToMapCol(self),
            Col(self, 'latitude', sDescription='<h2>Hallo</h2>'),
            Col(self, 'longitude'),
        ]
