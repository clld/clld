from clld.web.datatables.base import DataTable, Col, LinkCol, ExternalLinkCol
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import link, text2html
from clld.db.models.common import Contributor


class ContributionsCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        return HTML.ul(
            *[HTML.li(link(
                self.dt.req, c.contribution)) for c in item.contribution_assocs])


class AddressCol(Col):
    def format(self, item):
        return text2html(item.address)


class NameCol(LinkCol):
    def order(self):
        return Contributor.id


class UrlCol(ExternalLinkCol):
    def get_attrs(self, item):
        return {'label': 'homepage'}


class Contributors(DataTable):
    def col_defs(self):
        return [
            NameCol(self, 'name'),
            ContributionsCol(self, 'Contributions'),
            AddressCol(self, 'address'),
            UrlCol(self, 'Homepage'),
        ]
