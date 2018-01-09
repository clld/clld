"""Default DataTable for Sentence objects."""
from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from clld.db.util import get_distinct_values
from clld.db.models.common import (
    Language, Sentence, Parameter, ValueSentence, Value, ValueSet, Sentence_files,
)
from clld.web.datatables.base import (
    DataTable, LinkCol, DetailsRowLinkCol, Col,
)
from clld.web.util.helpers import icon


class TypeCol(Col):

    """Render the type attribute of a Sentence."""

    def __init__(self, dt, name, **kw):
        kw.setdefault('sTitle', dt.req.translate('Type'))
        kw.setdefault('choices', get_distinct_values(Sentence.type))
        super(TypeCol, self).__init__(dt, name, **kw)

    def search(self, qs):
        return Sentence.type == qs

    def format(self, item):
        return item.type

    def order(self):
        return Sentence.type


class TsvCol(Col):
    def search(self, qs):
        return super(TsvCol, self).search('\t'.join(qs.split()))


class AudioCol(Col):
    def __init__(self, dt, name, **kw):
        kw['choices'] = ['yes']
        kw['input-size'] = 'mini'
        kw['model_col'] = Sentence_files.id
        Col.__init__(self, dt, name, **kw)

    def format(self, item):
        if item.audio:
            return icon('volume-up')

    def order(self):
        return Sentence_files.id

    def search(self, qs):
        if qs == 'yes':
            return Sentence_files.pk != 0


class Sentences(DataTable):

    """Default DataTable for Sentence objects."""

    __constraints__ = [Parameter, Language]

    def base_query(self, query):
        query = query\
            .outerjoin(
                Sentence_files,
                and_(
                    Sentence_files.object_pk == Sentence.pk,
                    Sentence_files.mime_type.contains('audio/')))\
            .options(joinedload(Sentence._files))

        if self.language:
            query = query.filter(Sentence.language_pk == self.language.pk)
        else:
            query = query.join(Language).options(joinedload(Sentence.language))

        if self.parameter:
            query = query.join(ValueSentence, Value, ValueSet)\
                .filter(ValueSet.parameter_pk == self.parameter.pk)

        return query

    def col_defs(self):
        return [
            Col(self, 'id', bSortable=False, input_size='mini'),
            LinkCol(self, 'name', sTitle='Primary text', sClass="object-language"),
            TsvCol(self, 'analyzed', sTitle='Analyzed text'),
            TsvCol(self, 'gloss', sClass="gloss"),
            Col(self,
                'description',
                sTitle=self.req.translate('Translation'),
                sClass="translation"),
            TypeCol(self, 'type'),
            LinkCol(
                self,
                'language',
                model_col=Language.name,
                get_obj=lambda i: i.language,
                bSortable=not self.language,
                bSearchable=not self.language),
            DetailsRowLinkCol(self, 'd'),
        ]

    def get_options(self):
        return {'aaSorting': []}
