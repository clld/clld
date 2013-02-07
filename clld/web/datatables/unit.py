from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession
from clld.db.models.common import Unit, Language
from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol


class LanguageLinkCol(LinkCol):
    def get_obj(self, item):
        return item.language


class DescriptionLinkCol(LinkCol):
    def get_attrs(self, item):
        return {'label': item.description}


class Units(DataTable):

    def __init__(self, req, model, language=None, **kw):
        if language:
            self.language = language
        elif 'language' in req.params:
            self.language = Language.get(req.params['language'])
        else:
            self.language = None

        DataTable.__init__(self, req, model, **kw)

    def base_query(self, query):
        query = query.join(Language).options(joinedload(Unit.language))

        if self.language:
            return query.filter(Unit.language == self.language)
        return query

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            DescriptionLinkCol(self, 'description'),
            LanguageLinkCol(self, 'language', model_col=Language.name),
        ]

    def get_options(self):
        opts = DataTable.get_options(self)
        if self.language:
            opts['sAjaxSource'] = self.req.route_url('units', _query={'language': self.language.id})
            #opts["aaSorting"] = [[ 2, "asc" ]]
        return opts
