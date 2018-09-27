import pytest

from clld.web.util.glottolog import *


def test_url():
    assert url().endswith('glottolog.org')
    assert url('1').endswith('languoid/id/1')
    assert url('x', obj_type='reference').endswith('reference/id/x')

    with pytest.raises(AssertionError):
        url('x', obj_type='x')


def test_link(env):
    assert '.png' in link(env['request'], id='1')
