from clld.web.datatables.base import DataTable, Col, LinkCol
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import external_link
from clld.db.models.common import Contributor


class ContributionsCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return HTML.ul(
            *[HTML.li(HTML.a(c.contribution.name,
                             href=self.dt.req.resource_url(c.contribution)))
              for c in item.contribution_assocs]
        )


class NameCol(LinkCol):
    def order(self):
        return Contributor.id


class UrlCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return external_link(item.url, 'homepage') if item.url else ''


class Contributors(DataTable):
    def col_defs(self):
        return [
            NameCol(self, 'name'),
            ContributionsCol(self, 'Contributions'),
            Col(self, 'address'),
            UrlCol(self, 'Homepage'),
        ]
