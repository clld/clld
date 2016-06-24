from __future__ import unicode_literals, print_function, division, absolute_import
import os
from tempfile import mktemp
import gzip
from contextlib import closing
from xml.etree import cElementTree as et

from mock import Mock, patch
from clldutils.testing import WithTempDirMixin

from clld.db.models.common import Language, Source
from clld.tests.util import TestWithEnv, WithDbAndDataMixin


class Tests(WithDbAndDataMixin, WithTempDirMixin, TestWithEnv):
    def test_download_dir(self):
        from clld.web.adapters.download import download_dir

        assert download_dir('clld')

    def test_Download(self):
        from clld.web.adapters.download import Download

        dl = Download(Source, 'clld', ext='x')
        assert dl.asset_spec(Mock()).startswith('clld:')

        class TestDownload(Download):
            _path = mktemp()

            def asset_spec(self, req):
                return self._path

        dl = TestDownload(Source, 'clld', ext='bib')
        abspath = dl.abspath(self.env['request'])
        assert not abspath.exists()
        dl.create(self.env['request'], verbose=False)
        dl.size(self.env['request'])
        dl.label(self.env['request'])
        assert abspath.exists()
        os.remove(abspath.as_posix())

        dl = TestDownload(Source, 'clld', ext='rdf')
        dl.create(self.env['request'], verbose=False)
        os.remove(dl.abspath(self.env['request']).as_posix())

    def test_Download_url(self):
        from clld.web.adapters.download import Download

        with patch.multiple(
                'clld.web.adapters.download',
                download_asset_spec=Mock(
                    return_value='clld:web/static/images/favicon.ico')):
            dl = Download(Source, 'clld', ext='bib')
            assert dl.url(self.env['request'])

    def test_Download2(self):
        from clld.web.adapters.download import CsvDump, N3Dump, RdfXmlDump

        out = self.tmp_path('dl')
        dl = CsvDump(Language, 'clld')
        dl.create(self.env['request'], verbose=False, outfile=out)
        self.assertTrue(out.exists())
        dl.create(self.env['request'], filename=out, verbose=False, outfile=out)
        dl = N3Dump(Language, 'clld')
        self.assertEqual(dl.abspath(self.env['request']).name, 'dataset-language.n3.gz')
        dl.create(self.env['request'], verbose=False, outfile=out)
        dl = RdfXmlDump(Language, 'clld')
        dl.create(self.env['request'], verbose=False, outfile=out)

        with closing(gzip.open(out.as_posix(), 'rb')) as fp:
            assert et.fromstring(fp.read())
