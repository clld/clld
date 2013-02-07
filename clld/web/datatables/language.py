from clld.web.datatables.base import (
    DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol, IdCol,
)


class Languages(DataTable):
    def col_defs(self):
        return [
            DetailsRowLinkCol(self),
            IdCol(self, 'id'),
            LinkCol(self, 'name'),
            LinkToMapCol(self),
            Col(self, 'latitude', sDescription='<small>The geographic latitude</small>'),
            Col(self, 'longitude'),
        ]
