from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol


class Languages(DataTable):
    show_details = True

    def col_defs(self):
        return [
            DetailsRowLinkCol(self, route_name='language'),
            LinkCol(self, 'id', route_name='language', get_label=lambda item: item.id),
            LinkCol(self, 'name', route_name='language'),
            Col(self, 'latitude'),
            Col(self, 'longitude'),
        ]
