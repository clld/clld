from clld.web.util.doi import *


def test_url(mocker):
    assert url('xyz').endswith('xyz')
    assert url(mocker.Mock(doi='xyz')).endswith('xyz')

    class Obj:
        jsondata = dict(doi='xyz')

    assert url(Obj()).endswith('xyz')


def test_link(env):
    assert '.png' in link(env['request'], 'xyz')


def test_badge():
    assert badge('xyz')
    assert badge('10.5281/zenodo.xyz')
