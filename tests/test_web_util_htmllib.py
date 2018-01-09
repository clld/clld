from __future__ import unicode_literals


def test_HTML():
    from clld.web.util.htmllib import HTML

    assert 'class' in HTML.div(HTML.cdata(), class_='abc')
    assert str(HTML.a()) == '<a></a>'


def test_literal():
    from clld.web.util.htmllib import literal

    assert literal.escape('<div/>') == '&lt;div/&gt;'
