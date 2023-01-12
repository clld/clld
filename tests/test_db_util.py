
def test_compute_language_sources(data, persist):
    from clld.db.util import compute_language_sources
    from clld.db.models.common import Source, Sentence, Language, SentenceReference

    s = Sentence(id='sentenced', language=Language(id='newlang'))
    persist(SentenceReference(sentence=s, source=Source.first()))
    compute_language_sources()


def test_compute_number_of_values(data):
    from clld.db.util import compute_number_of_values
    compute_number_of_values()


def test_icontains(data):
    from clld.db.util import icontains
    from clld.db.models.common import Dataset
    from clld.db.meta import DBSession

    for qs, count in [('Se', 1), ('^d$', 0), ('^d', 1), ('setä$', 1), ('\\\\b', 0)]:
        q = DBSession.query(Dataset).filter(icontains(Dataset.name, qs))
        assert q.count() == count
