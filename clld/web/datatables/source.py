"""Default DataTable for Source objects."""
from clld.db.models.common import Language, LanguageSource, Source
from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol
from clld.lib.bibtex import EntryType


class TypeCol(Col):

    """Render the BibTeX type of a Source item."""

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

    """Default DataTable for Source objects."""

    __constraints__ = [Language]

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
