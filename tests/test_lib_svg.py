# coding: utf8
from __future__ import unicode_literals, print_function, division
from xml.etree.ElementTree import fromstring

import pytest

from clld.lib.svg import *


def test_icon():
    assert 'circle' in icon('c000000')
    assert 'opacity' in icon('tf00', opacity=0.5)


def test_pie():
    with pytest.raises(AssertionError):
        pie([1], [])

    assert 'circle' in pie([100], ['eee'], titles=['title'])
    assert 'circle' in pie([50, 0], ['eee', 'fff'])
    assert len(pie([50, 50, 0], ['fff', 'eee', 'fff']).split('<path ')) == 3
    assert len(pie([50, 50, 5], ['fff', 'eee', 'fff']).split('<path ')) == 4
    assert 'circle' not in pie([100, 20], ['eee', 'fff'])
    res = fromstring(pie([2, 7], ['eee', '111'], titles=['a', 'b'], stroke_circle='#f00'))
    assert res.tag == '{http://www.w3.org/2000/svg}svg'


def test_data_url():
    assert data_url(icon('d000')).startswith('data:')
