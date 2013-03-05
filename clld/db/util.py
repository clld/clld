from clld.db.meta import DBSession
from clld.db.models import common


def compute_language_sources(session=None):
    """compute relations between languages and sources by going through the more specific
    relations.
    """
    session = session or DBSession

    old_sl = {}
    for pair in session.query(common.LanguageSource):
        old_sl[(pair.source_pk, pair.language_pk)] = True

    sl = {}

    for ref in session.query(common.ValueReference):
        sl[(ref.source_pk, ref.value.language_pk)] = True

    for ref in session.query(common.SentenceReference):
        sl[(ref.source_pk, ref.sentence.language_pk)] = True

    for ref in session.query(common.ContributionReference):
        if hasattr(ref.contribution, 'language_pk'):
            sl[(ref.source_pk, ref.contribution.language_pk)] = True

    for s, l in sl:
        if (s, l) not in old_sl:
            session.add(common.LanguageSource(language_pk=l, source_pk=s))
