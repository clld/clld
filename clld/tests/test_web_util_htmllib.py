from __future__ import unicode_literals
import unittest


class Tests(unittest.TestCase):
    def test_HTML(self):
        from clld.web.util.htmllib import HTML

        self.assertTrue('class' in HTML.div(HTML.cdata(), class_='abc'))
        self.assertEqual(str(HTML.a()), '<a></a>')

    def test_literal(self):
        from clld.web.util.htmllib import literal

        self.assertEqual(literal.escape('<div/>'), '&lt;div/&gt;')
