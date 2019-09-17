
def test_add_renderer_globals(env, mocker):
    from clld.web.subscribers import add_renderer_globals

    ctx = {'renderer_name': 'path/base.ext.mako', 'request': None}
    add_renderer_globals(mocker.Mock(path_base_ext=lambda **kw: {'a': 3}), ctx)
    assert ctx['a'] == 3
