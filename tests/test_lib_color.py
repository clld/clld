# coding: utf8
from __future__ import unicode_literals, print_function, division

from clld.lib.color import *


def test_rgb_as_hex():
    assert rgb_as_hex('0e0f0e') == rgb_as_hex((14, 15, 14))
    assert rgb_as_hex('efe') == rgb_as_hex('#EEFFEE')
    assert rgb_as_hex((1.0, 0.0, 0.0)) == '#FF0000'


def test_is_bright():
    assert is_bright('fff')
    assert not is_bright('#000000')


def test_qualitative_colors():
    for n in [10, 20, 30]:
        assert len(qualitative_colors(n)) == n
    assert len(qualitative_colors(10, set='boynton')) == 10
    assert len(qualitative_colors(10, set='tol')) == 10


def test_sequential_colors():
    assert len(sequential_colors(8)) == 8


def test_diverging_colors():
    assert len(diverging_colors(10)) == 10
