import unittest

from mock import Mock, patch

from clld.tests.util import TESTS_DIR


class Tests(unittest.TestCase):
    def test_Result(self):
        from clld.lib.fmpxml import Result

        Result(file(TESTS_DIR.joinpath('fmpxmlresult.xml')).read())

    def test_normalize_markup(self):
        from clld.lib.fmpxml import normalize_markup
        self.assertEqual('a\nb', normalize_markup('a<BR>b'))
        self.assertEqual(normalize_markup(''), None)
        self.assertEqual(normalize_markup('<SPAN STYLE="clear: right;">b</SPAN>'), 'b')

    def test_Client(self):
        from clld.lib.fmpxml import Client

        r = Mock(text=file(TESTS_DIR.joinpath('fmpxmlresult.xml')).read().decode('utf8'))

        with patch('clld.lib.fmpxml.requests', Mock(get=lambda *a, **kw: r)):
            c = Client(None, None, None, None, verbose=False)
            c.get('stuff')
            c.get('stuff')
