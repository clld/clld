from clld.web.datatables.base import DataTable, Col, LinkCol
from clld.web.util.helpers import linked_contributors, button, JSModal


class ContributorsCol(Col):
    def __init__(self, dt, name='contributors', **kw):
        kw.setdefault('bSearchable', False)
        kw.setdefault('bSortable', False)
        super(ContributorsCol, self).__init__(dt, name, **kw)

    def format(self, item):
        return linked_contributors(self.dt.req, item)


class CitationCol(Col):
    def __init__(self, dt, name='cite', **kw):
        kw.setdefault('bSearchable', False)
        kw.setdefault('bSortable', False)
        super(CitationCol, self).__init__(dt, name, **kw)

    def format(self, item):
        return button(
            'cite',
            onclick=JSModal.show(item.name, self.dt.req.resource_url(item, ext='md.html'))
        )


class Contributions(DataTable):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            ContributorsCol(self),
            CitationCol(self),
        ]
