from sqlalchemy import asc, desc

from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import external_link
from clld.db.models.common import Contributor


class ContributionsCol(Col):
    def format(self, item):
        return HTML.ul(
            *[HTML.li(HTML.a(c.contribution.name, href=self.dt.req.route_url('contribution', id=c.contribution.id)))
              for c in item.contribution_assocs]
        )


class NameCol(Col):
    def order(self):
        return Contributor.id


class UrlCol(Col):
    def format(self, item):
        if item.url:
            return external_link(item.url, 'homepage')
        return ''


class Contributors(DataTable):
    def col_defs(self):
        return [
            NameCol(self, 'name'),
            ContributionsCol(self, 'Contributions', bSortable=False, bSearchable=False),
            UrlCol(self, 'Homepage', bSortable=False, bSearchable=False),
        ]
