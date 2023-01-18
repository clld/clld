from clld.web.util.htmllib import *


def test_HTML():
    assert 'class' in HTML.div(HTML.cdata(), class_='abc')
    assert str(HTML.a()) == '<a></a>'


def test_literal():
    assert literal.escape('<div/>') == '&lt;div/&gt;'
