from clld.web.util.concepticon import *


def test_url():
    assert url().endswith('concepticon.clld.org')
    assert url('1').endswith('parameters/1')
    assert url('x', obj_type='Concept').endswith('values/x')


def test_link(env):
    assert '.png' in link(env['request'], id='1')
    assert 'share' in link(env['request'], id='1', label='gloss')
