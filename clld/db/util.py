from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession
from clld.db.models import common


def icontains(col, qs):
    return col.ilike('%' + qs + '%')


def compute_language_sources(*references):
    """compute relations between languages and sources by going through the relevant
    models derived from the HasSource mixin.
    """
    old_sl = {}
    for pair in DBSession.query(common.LanguageSource):
        old_sl[(pair.source_pk, pair.language_pk)] = True

    references = list(references)
    references.extend([
        (common.ValueSetReference, 'valueset'),
        (common.SentenceReference, 'sentence')])
    sl = {}
    for model, attr in references:
        for ref in DBSession.query(model):
            sl[(ref.source_pk, getattr(ref, attr).language_pk)] = True

    for s, l in sl:
        if (s, l) not in old_sl:
            DBSession.add(common.LanguageSource(language_pk=l, source_pk=s))


def compute_number_of_values():
    """compute number of values per valueset and store it in valueset's jsondata.
    """
    for valueset in DBSession.query(common.ValueSet).options(
        joinedload(common.ValueSet.values)
    ):
        d = valueset.jsondata if valueset.jsondata else {}
        d['_number_of_values'] = len(valueset.values)
        valueset.jsondata = d


def get_distinct_values(col, key=None):
    return sorted([r[0] for r in DBSession.query(col).distinct() if r[0]], key=key)
