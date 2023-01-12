from clld.config import get_config


def test_get_config(testsdir):
    assert get_config(testsdir.joinpath('test.ini'))['app:main.custom_int'] == 5
