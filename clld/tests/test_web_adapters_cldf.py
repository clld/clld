# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import
from zipfile import ZipFile

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

        with ZipFile(tmp.as_posix()) as zip:
            self.assertIn('Wordlist-metadata.json', zip.namelist())
            zip.extractall(self.tmp_path('cldf').as_posix())

        ds = CldfDataset.from_metadata(self.tmp_path('cldf', 'Wordlist-metadata.json'))
        self.assertEqual(ds.module, 'Wordlist')
        values = list(ds[ds.primary_table])
        self.assertEqual(len(values), 3)
        for v in values:
            list(ds.sources.expand_refs(v['Source']))
