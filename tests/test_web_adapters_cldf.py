# coding: utf8
from __future__ import unicode_literals, print_function, division, absolute_import
from zipfile import ZipFile

from pycldf.dataset import Dataset as CldfDataset

from clld.db.meta import DBSession
from clld.db.models.common import Dataset, Source


def test_source2source(env):
    from clld.web.adapters.cldf import source2source

    for source in DBSession.query(Source):
        res = source2source(env['request'], source)
        assert len(res) >= 1


def test_CldfDownload(env, tmppath, mocker, capsys):
    from clld.web.adapters.cldf import CldfDownload

    mocker.patch('clld.web.adapters.cldf.transaction')
    tmp = tmppath / 'dl.zip'
    dl = CldfDownload(Dataset, 'clld')
    dl.create(env['request'], outfile=tmp, verbose=True)
    out, err = capsys.readouterr()
    assert 'Value' in out

    outdir = tmppath / 'cldf'
    with ZipFile(tmp.as_posix()) as zip:
        assert 'Wordlist-metadata.json' in zip.namelist()
        zip.extractall(str(outdir))

    ds = CldfDataset.from_metadata(outdir.joinpath('Wordlist-metadata.json'))
    assert ds.module == 'Wordlist'
    values = list(ds[ds.primary_table])
    assert len(values) == 3
    for v in values:
        list(ds.sources.expand_refs(v['Source']))
