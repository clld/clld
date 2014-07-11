from __future__ import unicode_literals, division, absolute_import, print_function
import unittest

from mock import Mock, patch


class Tests(unittest.TestCase):
    def _requests(self, json):
        return Mock(get=lambda *a, **kw: Mock(json=lambda: json))

    def test_resourcemap(self):
        from clld.lib.clld_api import resourcemap

        with patch(
            'clld.lib.clld_api.requests',
            self._requests({})
        ):
            resourcemap('localhost', 'language')
