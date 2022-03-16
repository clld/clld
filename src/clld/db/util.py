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
    'get_distinct_values', 'get_alembic_version', 'set_alembic_version', 'page_query']


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
        qs = spattern.sub('', qs)
        prefix = ''

    if epattern.search(qs):
        qs = epattern.sub('', qs)
        suffix = ''

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


def set_alembic_version(engine, db_version):
    """Sets up the alembic_version table in an sqlite database.

    .. notes::

        This function is only to be used with sqlite databases, either when testing or
        when restoring a frozen database.

    :param engine: A connection to an sqlite database.
    :param db_version: The new version_num.
    """
    engine.execute("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32))")
    if engine.execute("SELECT * FROM alembic_version").fetchall():  # pragma: no cover
        engine.execute("UPDATE alembic_version SET version_num = '%s'" % db_version)
    else:
        engine.execute("INSERT INTO alembic_version VALUES ('%s')" % db_version)


def get_alembic_version(engine):
    try:
        return engine.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    except:  # noqa: E722; # pragma: no cover
        return None
