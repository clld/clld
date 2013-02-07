from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol
from clld.web.util.helpers import linked_contributors, button, dumps, JSModal


class ContributorsCol(Col):
    def format(self, item):
        return linked_contributors(self.dt.req, item)


class CitationCol(Col):
    def format(self, item):
        return button(
            'cite',
            onclick=JSModal.show(item.name, self.dt.req.resource_url(item, ext='md.html'))
        )


class Contributions(DataTable):

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            ContributorsCol(self, 'contributors', bSearchable=False, bSortable=False),
            CitationCol(self, 'cite', bSearchable=False, bSortable=False)
        ]
