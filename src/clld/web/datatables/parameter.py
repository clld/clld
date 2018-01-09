"""Default DataTable for Parameter objects."""
from clld.web.datatables.base import DataTable, LinkCol, DetailsRowLinkCol


class Parameters(DataTable):

    """Default DataTable for Parameter objects."""

    def col_defs(self):
        return [
            DetailsRowLinkCol(self, 'd'),
            LinkCol(self, 'name'),
        ]
