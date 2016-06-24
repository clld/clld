# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from clld.tests.util import WithDbAndDataMixin


class Tests(WithDbAndDataMixin, unittest.TestCase):
    def test_compute_language_sources(self):
        from clld.db.util import compute_language_sources
        from clld.db.models.common import Source, Sentence, Language, SentenceReference
        from clld.db.meta import DBSession

        s = Sentence(id='sentenced', language=Language(id='newlang'))
        sr = SentenceReference(sentence=s, source=Source.first())
        DBSession.add(sr)
        DBSession.flush()
        compute_language_sources()

    def test_compute_number_of_values(self):
        from clld.db.util import compute_number_of_values
        compute_number_of_values()

    def test_icontains(self):
        from clld.db.util import icontains
        from clld.db.models.common import Dataset
        from clld.db.meta import DBSession

        for qs, count in [('Se', 1), ('^d$', 0), ('^d', 1), ('setä$', 1)]:
            q = DBSession.query(Dataset).filter(icontains(Dataset.name, qs))
            self.assertEqual(q.count(), count)

    def test_collkey(self):
        from clld.db.util import collkey
        from clld.db.models.common import Language

        collkey(Language.name)
