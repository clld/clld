from clld.db.models.common import Language, LanguageSource
from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol


class Sources(DataTable):
    def __init__(self, req, model, language=None, **kw):
        super(Sources, self).__init__(req, model, **kw)
        if language:
            self.language = language
        elif 'language' in req.params:
            self.language = Language.get(req.params['language'])
        else:
            self.language = None
        self.download_formats.append('bib')

    def base_query(self, query):
        if self.language:
            query = query.join(LanguageSource)\
                .filter(LanguageSource.language_pk == self.language.pk)
        return query

    def col_defs(self):
        return [
            DetailsRowLinkCol(self),
            LinkCol(self, 'name'),
            Col(self, 'description', sTitle='Title'),
            Col(self, 'year'),
            Col(self, 'author'),
        ]

    def get_options(self):
        opts = super(Sources, self).get_options()
        if self.language:
            opts['sAjaxSource'] = self.req.route_url(
                'sources', _query={'language': self.language.id})
        return opts
