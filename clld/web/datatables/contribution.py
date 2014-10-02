"""Default DataTable for Contribution objects."""
from clld.web.datatables.base import DataTable, Col, LinkCol
from clld.web.util.helpers import linked_contributors, cite_button


class ContributorsCol(Col):

    """Render links to the corresponding Contributors of a Contribution."""

    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return linked_contributors(self.dt.req, item)


class CitationCol(Col):

    """Render a cite-button."""

    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return cite_button(self.dt.req, item)


class Contributions(DataTable):

    """Default DataTable for Contribution objects."""

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            ContributorsCol(self, 'contributor'),
            CitationCol(self, 'cite'),
        ]
