# coding: utf8
from __future__ import unicode_literals, print_function, division
from xml.etree.ElementTree import fromstring


def test_pie():
    from clld.lib.svg import pie

    pie([100], ['eee'])
    res = fromstring(pie([2, 7], ['eee', '111']))
    assert res.tag == '{http://www.w3.org/2000/svg}svg'
