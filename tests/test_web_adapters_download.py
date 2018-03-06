from __future__ import unicode_literals, print_function, division, absolute_import
import os
from tempfile import mktemp
import gzip
from contextlib import closing
from xml.etree import cElementTree as et

from clldutils.path import Path

from clld.db.models.common import Language, Source
from clld.web.adapters.download import *


def test_download_dir():
    assert download_dir('clld')


def test_Download(mocker, env):
    dl = Download(Source, 'clld', ext='x')
    assert dl.asset_spec(mocker.Mock()).startswith('clld:')

    class TestDownload(Download):
        _path = mktemp()

        def asset_spec(self, req):
            return self._path

    dl = TestDownload(Source, 'clld', ext='bib')
    abspath = dl.abspath(env['request'])
    assert not abspath.exists()
    dl.create(env['request'], verbose=False)
    dl.size(env['request'])
    dl.label(env['request'])
    assert abspath.exists()
    os.remove(abspath.as_posix())

    dl = TestDownload(Source, 'clld', ext='rdf')
    dl.create(env['request'], verbose=False)
    os.remove(dl.abspath(env['request']).as_posix())


def test_Download_url(mocker, env):
    mocker.patch.multiple(
        'clld.web.adapters.download',
        download_asset_spec=mocker.Mock(
            return_value='clld:web/static/images/favicon.ico'))
    dl = Download(Source, 'clld', ext='bib')
    assert dl.url(env['request'])


def test_Download2(env, tmppath):
    out = tmppath / 'dl'
    dl = CsvDump(Language, 'clld')
    dl.create(env['request'], verbose=False, outfile=out)
    assert out.exists()
    dl.create(env['request'], filename=out, verbose=False, outfile=out)
    dl = N3Dump(Language, 'clld')
    assert dl.abspath(env['request']).name == 'dataset-language.n3.gz'
    dl.create(env['request'], verbose=False, outfile=out)
    dl = RdfXmlDump(Language, 'clld')
    dl.create(env['request'], verbose=False, outfile=out)

    with closing(gzip.open(out.as_posix(), 'rb')) as fp:
        assert et.fromstring(fp.read())
