import logging

import pytest

from clld.__main__ import main


def test_create_downloads(testsdir):
    main(['create_downloads', '-l', str(testsdir / 'test.ini'), 'abc'],
         log=logging.getLogger(__name__))


def test_create(tmppath):
    outdir = tmppath / 'app'
    main(['create', '--quiet', str(outdir)])
    assert outdir.joinpath('setup.py').exists()
    with pytest.raises(ValueError):
        main(['create', '--quiet', str(outdir)])
    main(['create', '--quiet', '--force', str(outdir), "domain=example.org"])
    assert "example.org" in outdir.joinpath(
        'app', 'scripts', 'initializedb.py').read_text(encoding='utf8')


def test_initdb(tmppath):
    tmppath.joinpath('tests').mkdir()
    cfg = tmppath / 'tests' / 'test.ini'
    cfg.write_text("""\
[app:main]
use = call:testutils:main
sqlalchemy.url = sqlite:///{}
    """.format(tmppath / 'db.sqlite'), encoding='utf8')
    main(['initdb', str(cfg)])

    with pytest.raises(ValueError):
        main(['initdb', str(tmppath / 'xyz.ini')])
