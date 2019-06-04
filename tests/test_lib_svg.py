import warnings


def _import():
    from clld.lib.svg import pie
    return pie

def test_svg():
    with warnings.catch_warnings(record=True) as w:
        _import()
        assert issubclass(w[-1].category, DeprecationWarning)
