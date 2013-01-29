from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol
from clld.web.util.helpers import linked_contributors, button, dumps


class ContributorsCol(Col):
    def format(self, item):
        return linked_contributors(self.dt.req, item)


class CitationCol(Col):
    def format(self, item):
        return button('cite', onclick="CLLD.Modal.show(%s, %s)" % \
                      (dumps(item.name), dumps(self.dt.req.route_url('contribution_alt', id=item.id, ext='md.html'))))


class Contributions(DataTable):

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            ContributorsCol(self, 'contributors', bSearchable=False, bSortable=False),
            CitationCol(self, 'cite', bSearchable=False, bSortable=False)
        ]
