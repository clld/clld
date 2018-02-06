# coding: utf8
from __future__ import unicode_literals, print_function, division


def test_imports():
    from clld import scaffolds
    from clld.scripts import cli
    from clld.scripts import internetarchive
    assert scaffolds and cli and internetarchive
