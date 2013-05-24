from __future__ import unicode_literals

from clld.tests.util import TestWithDbAndData


class Tests(TestWithDbAndData):
    def test_compute_language_sources(self):
        from clld.db.util import compute_language_sources
        compute_language_sources()

    def test_compute_number_of_values(self):
        from clld.db.util import compute_number_of_values
        compute_number_of_values()
