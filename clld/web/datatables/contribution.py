from clld.web.datatables.base import DataTable, Col, LinkCol
from clld.web.util.helpers import linked_contributors, cite_button


class ContributorsCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return linked_contributors(self.dt.req, item)


class CitationCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return cite_button(self.dt.req, item)


class Contributions(DataTable):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            ContributorsCol(self, 'contributor'),
            CitationCol(self, 'cite'),
        ]
