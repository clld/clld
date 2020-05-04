import logging

from clld.__main__ import main


def test_create_downloads(testsdir):
    main(['create_downloads', '-l', str(testsdir / 'test.ini')], log=logging.getLogger(__name__))
