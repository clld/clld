"""Default DataTable for Language objects."""
from clld.web.datatables.base import DataTable, Col, LinkCol, LinkToMapCol, IdCol


class Languages(DataTable):

    """Default DataTable for Language objects."""

    def col_defs(self):
        return [
            IdCol(self, 'id'),
            LinkCol(self, 'name'),
            LinkToMapCol(self, 'm'),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
        ]
