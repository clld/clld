# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from mock import Mock

from clld.tests.util import TestWithEnv, WithDbAndDataMixin
from clld.db.models import common


class Tests(WithDbAndDataMixin, TestWithEnv):
    def _run(self, **kw):
        from clld.web.datatables.sentence import Sentences
        self.handle_dt(Sentences, common.Sentence, **kw)

    def test_plain(self):
        self._run()

        self.set_request_properties(params={
            'sSearch_5': 'x',
            'sSearch_2': ' ',
            'iSortingCols': '1',
            'iSortCol_0': '5',
            'sSortDir_0': 'desc',
        })
        self._run()

        self.set_request_properties(params={
            'sSearch_4': 'text',
            'iSortingCols': '1',
            'iSortCol_0': '4',
            'sSortDir_0': 'desc'})
        self._run()

    def test_with_language(self):
        self._run(language=common.Language.first())

    def test_with_parameter(self):
        self.set_request_properties(params={'parameter': 'parameter'})
        self._run()

    def test_AudioCol(self):
        from clld.web.datatables.sentence import AudioCol, Sentences

        col = AudioCol(Sentences(self.env['request'], common.Sentence), 'audio')
        col.order()
        col.search('yes')
        col.format(Mock())
