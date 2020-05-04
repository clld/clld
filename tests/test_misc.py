
def test_imports():
    from clld import scaffolds
    from clld.scripts import cli
    assert scaffolds and cli
