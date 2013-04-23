from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_Units(self):
        from clld.web.datatables.sentence import Sentences

        self.handle_dt(Sentences, common.Sentence)

        self.set_request_properties(params={
            'sSearch_5': 'x',
            'iSortingCols': '1',
            'iSortCol_0': '5',
            'sSortDir_0': 'desc',
        })
        self.handle_dt(Sentences, common.Sentence)
