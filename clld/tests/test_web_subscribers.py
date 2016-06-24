# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from mock import Mock

from clld.tests.util import TestWithEnv


class Tests(TestWithEnv):
    def test_add_renderer_globals(self):
        from clld.web.subscribers import add_renderer_globals

        ctx = {'renderer_name': 'path/base.ext.mako', 'request': None}
        add_renderer_globals(Mock(path_base_ext=lambda **kw: {'a': 3}), ctx)
        self.assertEqual(ctx['a'], 3)
