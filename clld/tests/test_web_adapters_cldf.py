# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from pycldf.dataset import Dataset as CldfDataset

from clld.db.models.common import Dataset
from clld.tests.util import TestWithEnv


class CldfTests(TestWithEnv):
    def test_CldfDownload(self):
        from clld.web.adapters.cldf import CldfDownload

        tmp = self.tmp_path('dl.zip')
        dl = CldfDownload(Dataset, 'clld')
        dl.create(self.env['request'], verbose=False, outfile=tmp)
        ds = CldfDataset.from_zip(tmp)
        self.assertEqual(ds.name, 'dataset-contribution-contribution')
        self.assertEqual(
            'http://localhost/languages/{Language_ID}',
            ds.table.schema.columns['Language_ID'].valueUrl)
        self.assertEqual(len(ds.rows), 3)
