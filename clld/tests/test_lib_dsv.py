# coding: utf8
from __future__ import unicode_literals
from unittest import TestCase
from StringIO import StringIO


class Tests(TestCase):
    def test_namedtuples_from_csv(self):
        from clld.lib.dsv import namedtuples_from_csv

        fp = StringIO('a,b\n1,2')
        assert list(namedtuples_from_csv(fp))[0].b == '2'
