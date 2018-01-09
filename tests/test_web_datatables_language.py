# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from clld.db.models import common

from testutils import handle_dt


def test_Languages(env):
    from clld.web.datatables.language import Languages

    handle_dt(env['request'], Languages, common.Language)
