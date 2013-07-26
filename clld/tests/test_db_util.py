from __future__ import unicode_literals

from clld.tests.util import TestWithDbAndData


class Tests(TestWithDbAndData):
    def test_compute_language_sources(self):
        from clld.db.models.common import Source, Sentence, Language, SentenceReference
        from clld.db.meta import DBSession
        from clld.db.util import compute_language_sources

        s = Sentence(id='sentenced', language=Language(id='newlang'))
        sr = SentenceReference(sentence=s, source=Source.first())
        DBSession.add(sr)
        DBSession.flush()
        compute_language_sources()

    def test_compute_number_of_values(self):
        from clld.db.util import compute_number_of_values
        compute_number_of_values()
