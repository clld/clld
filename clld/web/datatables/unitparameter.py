from clld.web.datatables.base import DataTable, Col


class Unitparameters(DataTable):
    def col_defs(self):
        return [Col(self, 'name')]
