# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import

from pycldf.dataset import Dataset as CldfDataset
from clldutils.testing import WithTempDirMixin

from clld.db.meta import DBSession
from clld.db.models.common import Dataset, Source
from clld.tests.util import TestWithEnv, WithDbAndDataMixin


class CldfTests(WithDbAndDataMixin, WithTempDirMixin, TestWithEnv):
    def test_source2source(self):
        from clld.web.adapters.cldf import source2source

        for source in DBSession.query(Source):
            res = source2source(self.env['request'], source)
            self.assertTrue(len(res) >= 1)

    def test_CldfDownload(self):
        from clld.web.adapters.cldf import CldfDownload

        tmp = self.tmp_path('dl.zip')
        dl = CldfDownload(Dataset, 'clld')
        dl.create(self.env['request'], verbose=False, outfile=tmp)
        ds = CldfDataset.from_zip(tmp)
        self.assertEqual(ds.name, 'dataset-contribution-contribution')
        self.assertEqual(
            'http://localhost/values/{ID}',
            ds.table.schema.aboutUrl)
        self.assertEqual(
            'http://localhost/languages/{Language_ID}',
            ds.table.schema.columns['Language_ID'].valueUrl)
        self.assertEqual(len(ds.rows), 3)
        self.assertIn('Language_glottocode', ds[0])
        self.assertIn('10-20', ds['value2']['Source'])
