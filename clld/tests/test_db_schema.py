from __future__ import unicode_literals

import unittest

from clld.tests.util import TESTS_DIR, dbschema

OUTFILE = TESTS_DIR / 'dbschema.sql'


class Tests(unittest.TestCase):
    """Dump the SQL produced by Base.metadata.create_all() for inspection."""

    def test_dbschema(self, filepath=OUTFILE, encoding='utf-8'):
        sql = dbschema()
        with filepath.open('w', encoding=encoding) as f:
            f.write(sql)
