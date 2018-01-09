# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

import pytest

from clld.web import datatables
from clld.db.models.common import Language, Value, Sentence
from clld.web.adapters.excel import Languages, Values, Sentences


@pytest.mark.parametrize(
    "adapter,model,datatable",
    [
        (Languages, Language, datatables.Languages),
        (Values, Value, datatables.Values),
        (Sentences, Sentence, datatables.Sentences),
    ])
def test_adapter(env, adapter, model, datatable):
    adapter(None).render_to_response(datatable(env['request'], model), env['request'])
