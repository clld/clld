from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol


class Sources(DataTable):
    def __init__(self, req, model, **kw):
        super(Sources, self).__init__(req, model, **kw)
        self.download_formats.append('bib')

    def col_defs(self):
        return [
            DetailsRowLinkCol(self),
            LinkCol(self, 'name'),
            Col(self, 'description', sTitle='Title'),
            Col(self, 'year'),
            Col(self, 'authors'),
        ]
