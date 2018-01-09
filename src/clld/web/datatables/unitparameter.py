"""Default DataTable for UnitParameter objects."""
from clld.web.datatables.base import DataTable, LinkCol


class Unitparameters(DataTable):

    """Default DataTable for UnitParameter objects."""

    def col_defs(self):
        return [LinkCol(self, 'name')]
