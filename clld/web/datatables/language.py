from clld.web.datatables.base import (
    DataTable, Col, LinkCol, DetailsRowLinkCol, LinkToMapCol, IdCol,
)


class DegreeCol(Col):
    __kw__ = {'sClass': 'right'}

    def format(self, item):
        val = getattr(item, self.name)
        if val:
            return '{0:.2f}'.format(val)
        return ''


class Languages(DataTable):
    def col_defs(self):
        return [
            #DetailsRowLinkCol(self, 'd'),
            IdCol(self, 'id'),
            LinkCol(self, 'name'),
            LinkToMapCol(self, 'm'),
            DegreeCol(self, 'latitude', sDescription='<small>The geographic latitude</small>'),
            DegreeCol(self, 'longitude', sDescription='<small>The geographic longitude</small>'),
        ]
