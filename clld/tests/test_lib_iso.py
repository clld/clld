from __future__ import unicode_literals, division, absolute_import, print_function
import unittest

from mock import Mock, patch


class Tests(unittest.TestCase):
    def _requests(self, c):
        return Mock(get=lambda *a, **kw: Mock(content=c))

    def test_get_taburls(self):
        from clld.lib.iso import get_taburls

        with patch(
            'clld.lib.iso.requests',
            self._requests('<a href="iso-639-3-macrolanguages_20121971.tab">a</a>')
        ):
            get_taburls()

    def test_get__tab(self):
        from clld.lib.iso import get_tab

        with patch.multiple(
            'clld.lib.iso',
            requests=self._requests('a\tb\nc\td\naa'),
            get_taburls=Mock(return_value={'name': 'path'})
        ):
            res = list(get_tab('name'))
            assert res[-1].b is None

    def test_get_documentation(self):
        from clld.lib.iso import get_documentation

        with patch(
            'clld.lib.iso.requests',
            self._requests('<h1>yyy</h1><table><tr><td/><td/></tr></table>')
        ):
            get_documentation('yyy')
