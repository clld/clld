from clld.db.models.common import Language, LanguageSource, Source
from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol
from clld.lib.bibtex import EntryType


class TypeCol(Col):
    def __init__(self, dt, name, *args, **kw):
        kw['sTitle'] = 'BibTeX type'
        kw['choices'] = [(t.value, t.description) for t in EntryType]
        super(TypeCol, self).__init__(dt, name, *args, **kw)

    def format(self, item):
        return getattr(item.bibtex_type, 'description', '')

    def order(self):
        return Source.bibtex_type

    def search(self, qs):
        return Source.bibtex_type == getattr(EntryType, qs)


class Sources(DataTable):
    def __init__(self, req, model, language=None, **kw):
        super(Sources, self).__init__(req, model, **kw)
        if language:
            self.language = language
        elif 'language' in req.params:
            self.language = Language.get(req.params['language'])
        else:
            self.language = None

    def base_query(self, query):
        if self.language:
            query = query.join(LanguageSource)\
                .filter(LanguageSource.language_pk == self.language.pk)
        return query

    def col_defs(self):
        return [
            DetailsRowLinkCol(self, 'd'),
            LinkCol(self, 'name'),
            Col(self, 'description', sTitle='Title'),
            Col(self, 'year'),
            Col(self, 'author'),
            TypeCol(self, 'bibtex_type'),
        ]

    def xhr_query(self):
        if self.language:
            return {'language': self.language.id}
