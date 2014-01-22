import time

from sqlalchemy.orm import joinedload
import transaction

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
        valueset.update_jsondata(_number_of_values=len(valueset.values))


def get_distinct_values(col, key=None):
    return sorted([r[0] for r in DBSession.query(col).distinct() if r[0]], key=key)


def page_query(q, n=1000, verbose=False, commit=False):
    """
    http://stackoverflow.com/a/1217947
    """
    s = time.time()
    offset = 0
    while True:
        r = False
        for elem in q.limit(n).offset(offset):
            r = True
            yield elem
        if commit:  # pragma: no cover
            transaction.commit()
            transaction.begin()
        offset += n
        e = time.time()
        if verbose:
            print e - s, offset, 'done'  # pragma: no cover
        s = e
        if not r:
            break
