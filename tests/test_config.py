from clld.config import get_config


def test_get_config(testsdir):
    cfg = get_config(testsdir.joinpath('test.ini'))
    assert cfg['app:main.custom_int'] == 5
