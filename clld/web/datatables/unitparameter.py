from clld.web.datatables.base import DataTable, LinkCol


class Unitparameters(DataTable):
    def col_defs(self):
        return [LinkCol(self, 'name')]
