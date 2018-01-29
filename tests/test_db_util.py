# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def test_alembic_version(db):
    from clld.db.util import set_alembic_version, get_alembic_version

    assert get_alembic_version(db) != '1234'
    set_alembic_version(db, '1234')
    assert get_alembic_version(db) == '1234'


def test_compute_language_sources(data):
    from clld.db.util import compute_language_sources
    from clld.db.models.common import Source, Sentence, Language, SentenceReference
    from clld.db.meta import DBSession

    s = Sentence(id='sentenced', language=Language(id='newlang'))
    sr = SentenceReference(sentence=s, source=Source.first())
    DBSession.add(sr)
    DBSession.flush()
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


def test_collkey(data):
    from clld.db.util import collkey
    from clld.db.models.common import Language

    collkey(Language.name)
