from __future__ import unicode_literals


def test_dbschema(dbschema):
    assert 'domainelement_files_history' in dbschema
