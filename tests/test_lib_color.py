import warnings


def _import():
    from clld.lib.color import sequential_colors
    return sequential_colors

def test_color():
    with warnings.catch_warnings(record=True) as w:
        _import()
        assert issubclass(w[-1].category, DeprecationWarning)