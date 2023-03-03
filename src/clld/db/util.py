"""Database utilities."""
import re
import time
import functools

from sqlalchemy import Integer
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import cast
import transaction

from clld.db.meta import DBSession
from clld.db.models import common

__all__ = [
    'as_int', 'contains', 'icontains', 'compute_language_sources', 'compute_number_of_values',
    'get_distinct_values', 'page_query']


def as_int(col):
    return cast(col, Integer)


def _contains(method, col, qs):
    """Infix search condition.

    Basic support is provided for specifying matches at beginning or end of the text.
    In addition, every special search syntax recognized by the ``LIKE`` operator of the
    underlying SQL dialect will work. Thus, to match strings with a specific <prefix>
    and <suffix>, a query string of the form "^<prefix>%<suffix>$" will do on PostgreSQL.

    .. seealso:: https://www.postgresql.org/docs/9.1/static/functions-matching.html
    """
    spattern = re.compile(r'^(\^|\\b)')
    epattern = re.compile(r'(\$|\\b)$')

    prefix, suffix = '%', '%'
    if spattern.search(qs):
        qs, prefix = spattern.sub('', qs), ''

    if epattern.search(qs):
        qs, suffix = epattern.sub('', qs), ''

    # Prevent invalid LIKE patterns:
    if qs.endswith('\\') and not qs.endswith('\\\\'):
        qs += '\\'
    return getattr(col, method)(prefix + qs + suffix)


icontains = functools.partial(_contains, 'ilike')
contains = functools.partial(_contains, 'like')


def compute_language_sources(*references):
    """compute relations between languages and sources.

    by going through the relevant models derived from the HasSource mixin.
    """
    old_sl = {(ls.source_pk, ls.language_pk) for ls in DBSession.query(common.LanguageSource)}

    references = list(references)
    references.extend([
        (common.ValueSetReference, 'valueset'),
        (common.SentenceReference, 'sentence')])

    for model, attr in references:
        for ref in DBSession.query(model):
            source_pk = ref.source_pk
            language_pk = getattr(ref, attr).language_pk
            if (source_pk, language_pk) not in old_sl:
                old_sl.add((source_pk, language_pk))
                DBSession.add(common.LanguageSource(
                    language_pk=language_pk, source_pk=source_pk))


def compute_number_of_values():
    """compute number of values per valueset and store it in valueset's jsondata."""
    for valueset in DBSession.query(common.ValueSet).options(
        joinedload(common.ValueSet.values)
    ):
        valueset.update_jsondata(_number_of_values=len(valueset.values))


def get_distinct_values(col, key=None):
    return sorted((c for c, in DBSession.query(col).distinct() if c), key=key)


def page_query(q, n=1000, verbose=False, commit=False):
    """Go through query results in batches.

    .. seealso:: http://stackoverflow.com/a/1217947
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
            print(e - s, offset, 'done')  # pragma: no cover
        s = e
        if not r:
            break
