from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession
from clld.db.models import common


def icontains(col, qs):
    return col.ilike('%' + qs + '%')


def compute_language_sources(session=None):
    """compute relations between languages and sources by going through the more specific
    relations.
    """
    session = session or DBSession

    old_sl = {}
    for pair in session.query(common.LanguageSource):
        old_sl[(pair.source_pk, pair.language_pk)] = True

    sl = {}

    for ref in session.query(common.ValueSetReference):
        sl[(ref.source_pk, ref.valueset.language_pk)] = True

    for ref in session.query(common.SentenceReference):
        sl[(ref.source_pk, ref.sentence.language_pk)] = True

    for ref in session.query(common.ContributionReference):
        if hasattr(ref.contribution, 'language_pk'):
            sl[(ref.source_pk, ref.contribution.language_pk)] = True

    for s, l in sl:
        if (s, l) not in old_sl:
            session.add(common.LanguageSource(language_pk=l, source_pk=s))


def compute_number_of_values(session=None):
    """compute number of values per valueset and store it in valueset's jsondata.
    """
    session = session or DBSession

    for valueset in session.query(common.ValueSet).options(
        joinedload(common.ValueSet.values)
    ):
        d = valueset.jsondata if valueset.jsondata else {}
        d['_number_of_values'] = len(valueset.values)
        valueset.jsondata = d


def get_distinct_values(col, session=None):
    session = session or DBSession
    return sorted([r[0] for r in session.query(col).distinct() if r[0]])
