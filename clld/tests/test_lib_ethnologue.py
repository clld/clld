from __future__ import unicode_literals, division, absolute_import, print_function
import unittest

from mock import Mock, patch


class Tests(unittest.TestCase):
    def _requests(self, c):
        return Mock(get=lambda *a, **kw: Mock(content=c))

    def test_get_subgroups(self):
        from clld.lib.ethnologue import get_subgroups

        with patch(
            'clld.lib.ethnologue.requests',
            self._requests('<a href="/subgroups/sid">S Name (5)</a>')
        ):
            res = get_subgroups()
            assert 'S Name' in res

    def test_get_classification(self):
        from clld.lib.ethnologue import get_classification

        get_classification(
            'group',
            '<li><a href="/subgroups/sid">S Name (1)</a><a href="/language/abc">[abc]</a>'
            '</li>')
