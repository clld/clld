from __future__ import unicode_literals, print_function, division, absolute_import
import os
from tempfile import mktemp
import gzip
from contextlib import closing
from xml.etree import cElementTree as et

from mock import Mock, MagicMock, patch
from clldutils.misc import UnicodeMixin

from clld.db.models.common import Language, Source, Dataset
from clld.tests.util import TestWithEnv


class Tests(TestWithEnv):
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

    def testDownload_url(self):
        from clld.web.adapters.download import Download

        with patch.multiple(
                'clld.web.adapters.download',
                download_asset_spec=Mock(
                    return_value='clld:web/static/images/favicon.ico')):
            dl = Download(Source, 'clld', ext='bib')
            assert dl.url(self.env['request'])

    def testDownload2(self):
        from clld.web.adapters.download import CsvDump, N3Dump, RdfXmlDump
        from clld.web.adapters.cldf import CldfDownload

        tmp = mktemp()

        class Path(MagicMock, UnicodeMixin):
            @property
            def stem(self):
                return 'a'

            @property
            def parent(self):
                return Mock(exists=Mock(return_value=False))

            def open(self, mode):
                return open(tmp, mode)

        with patch.multiple(
            'clld.web.adapters.cldf',
            ZipFile=MagicMock(),
            Path=MagicMock(return_value=Path()),
            move=Mock(),
            remove=Mock(),
        ):
            with patch(
                'clld.web.adapters.download.Path',
                new=MagicMock(return_value=Path()),
            ):
                dl = CldfDownload(Dataset, 'clld')
                dl.create(self.env['request'], verbose=False)

        with patch.multiple(
            'clld.web.adapters.download',
            ZipFile=MagicMock(),
            Path=MagicMock(return_value=Path()),
            move=Mock(),
            remove=Mock(),
        ):
            dl = CsvDump(Language, 'clld')
            dl.create(self.env['request'], verbose=False)
            dl.create(self.env['request'], filename='name.n3', verbose=False)
            dl = N3Dump(Language, 'clld')
            dl.create(self.env['request'], verbose=False)
            if os.path.exists(tmp):
                os.remove(tmp)
            else:  # pragma: no cover
                raise ValueError
            dl = RdfXmlDump(Language, 'clld')
            dl.create(self.env['request'], verbose=False)

        with closing(gzip.open(tmp, 'rb')) as fp:
            assert et.fromstring(fp.read())

        if os.path.exists(tmp):
            os.remove(tmp)
        else:  # pragma: no cover
            raise ValueError
