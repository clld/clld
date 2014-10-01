# coding: utf8
from __future__ import absolute_import, print_function, division, unicode_literals
from unittest import TestCase
import tempfile
import os
from io import open


class Tests(TestCase):
    def test_entry(self):
        from clld.lib.sfm import Entry

        e = Entry([('lx', 'a'), ('lx', 'b')])
        self.assertEqual(e.get('lx'), 'a')
        self.assertEqual(e.getall('lx'), ['a', 'b'])
        self.assertIsNone(e.get('ll'))
        self.assertEqual(e.markers(), set(['lx']))
        self.assert_(e.__unicode__())

    def test_Dictionary(self):
        from clld.lib.sfm import Dictionary

        c = "\\_md x\r\n\\lx ml\r\nlemma\r\n\\ge gloss\r\n\r\n\\lx äöüß\r\n\\ge gloss 2"
        tmp = tempfile.mktemp()
        with open(tmp, mode='wb') as fp:
            fp.write(c.encode('utf8'))

        try:
            db = Dictionary(tmp)
            self.assertEqual(len(db.entries), 2)
            self.assertEqual(db.markers(), set(['lx', 'ge']))
            self.assertIn('ml\nlemma', db.values('lx'))
            self.assertIn('äöüß', db.values('lx'))
        finally:
            os.remove(tmp)
