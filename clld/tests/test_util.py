from __future__ import unicode_literals


def test_slug():
    from clld.util import slug

    assert slug('A B. \xe4C') == 'abac'
