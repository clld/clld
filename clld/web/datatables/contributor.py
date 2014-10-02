"""Default DataTable for Contributor objects."""
from clld.web.datatables.base import DataTable, Col, LinkCol, ExternalLinkCol
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import link, text2html
from clld.db.models.common import Contributor


class ContributionsCol(Col):

    """Render a list of contributions a Contributor has participated in."""

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

    """Render a link to a Contributor's homepage."""

    def get_attrs(self, item):
        return {'label': 'homepage'}


class Contributors(DataTable):

    """Default DataTable for Contributor objects."""

    def col_defs(self):
        return [
            NameCol(self, 'name'),
            ContributionsCol(self, 'Contributions'),
            AddressCol(self, 'address'),
            UrlCol(self, 'Homepage'),
        ]
