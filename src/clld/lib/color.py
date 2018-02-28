# coding: utf8
from __future__ import unicode_literals, print_function, division
import colorsys
import itertools
from fractions import Fraction
import math
try:  # pragma: no cover
    from itertools import imap as map
except ImportError:  # pragma: no cover
    pass

from six import string_types

__all__ = [
    'brightness',
    'is_bright',
    'rgb_as_hex',
    'diverging_colors',
    'qualitative_colors',
    'sequential_colors'
]


def _to_rgb(s):
    def f2i(d):
        assert 0 <= d <= 1
        res = int(math.floor(d * 256))
        if res == 256:
            res = 255
        return res

    if isinstance(s, (tuple, list)):
        assert len(s) == 3
        if isinstance(s[0], (float, Fraction)):
            s = [f2i(d) for d in s]
        return s
    assert isinstance(s, string_types)
    if s.startswith('#'):
        s = s[1:]
    if len(s) == 3:
        s = ''.join(c + c for c in s)
    assert len(s) == 6
    return tuple(int(c, 16) for c in [s[i:i + 2] for i in range(0, 6, 2)])


def rgb_as_hex(s):
    return '#{0:02X}{1:02X}{2:02X}'.format(*_to_rgb(s))


def brightness(color):
    """
    see https://www.w3.org/TR/AERT/#color-contrast
    """
    R, G, B = _to_rgb(color)
    return 0.299 * R + 0.587 * G + 0.114 * B


def is_bright(color):
    # 125 seems to be a common cut-off above which to regard a color as "bright".
    return brightness(color) > 125


def qualitative_colors(n, set=None):
    if n <= 11 and set == 'boynton':
        # R. M. Boynton. Eleven colors that are almost never confused.
        # In B. E. Rogowitz, editor,
        # Proceedings of the SPIE Symposium: Human Vision, Visual Processing, and Digital
        # Display, volume 1077, pages 322{332, Bellingham, WA, 1989.
        # SPIE Int. Soc. Optical Engineering.
        return [
            rgb_as_hex(c) for c in
            [
                (91, 0, 13),
                (0, 255, 223),
                (23, 169, 255),
                (255, 232, 0),
                (8, 0, 91),
                (255, 208, 198),
                (4, 255, 4),
                (0, 0, 255),
                (0, 79, 0),
                (255, 21, 205),
                (255, 0, 0),
            ][:n]]
    if n <= 12 and set == 'tol':
        # https://personal.sron.nl/~pault/colourschemes.pdf
        # as implemented by drmccloy here https://github.com/drammock/colorblind
        cols = ['#4477AA', '#332288', '#6699CC', '#88CCEE', '#44AA99', '#117733',
                '#999933', '#DDCC77', '#661100', '#CC6677', '#AA4466', '#882255',
                '#AA4499']
        indices = [[0],
                   [0, 9],
                   [0, 7, 9],
                   [0, 5, 7, 9],
                   [1, 3, 5, 7, 9],
                   [1, 3, 5, 7, 9, 12],
                   [1, 3, 4, 5, 7, 9, 12],
                   [1, 3, 4, 5, 6, 7, 9, 12],
                   [1, 3, 4, 5, 6, 7, 9, 11, 12],
                   [1, 3, 4, 5, 6, 7, 8, 9, 11, 12],
                   [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12],
                   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
        return [cols[ix] for ix in indices[n - 1]]

    if n <= 22:
        # theory:
        # https://eleanormaclure.files.wordpress.com/2011/03/colour-coding.pdf (page 5)
        # kelly's colors:
        #  https://i.kinja-img.com/gawker-media/image/upload/1015680494325093012.JPG
        return [
            rgb_as_hex(c) for c in
            [
                'F2F3F4',
                '222222',
                'F3C300',
                '875692',
                'F38400',
                'A1CAF1',
                'BE0032',
                'C2B280',
                '848482',
                '008856',
                'E68FAC',
                '0067A5',
                'F99379',
                '604E97',
                'F6A600',
                'B3446C',
                'DCD300',
                '882D17',
                '8DB600',
                '654522',
                'E25822',
                '2B3D26'][:n]
        ]

    #
    # taken from https://stackoverflow.com/a/13781114
    #
    def zenos_dichotomy():
        """
        http://en.wikipedia.org/wiki/1/2_%2B_1/4_%2B_1/8_%2B_1/16_%2B_%C2%B7_%C2%B7_%C2%B7
        """
        for k in itertools.count():
            yield Fraction(1, 2**k)

    def getfracs():
        yield 0
        for k in zenos_dichotomy():
            i = k.denominator  # [1,2,4,8,16,...]
            for j in range(1, i, 2):
                yield Fraction(j, i)

    def genhsv(h):
        for s in [Fraction(6, 10)]:  # optionally use range
            for v in [Fraction(8, 10), Fraction(5, 10)]:  # could use range too
                yield (h, s, v)  # use bias for v here if you use range

    def gethsvs():
        return itertools.chain.from_iterable(map(genhsv, getfracs()))

    return [
        rgb_as_hex(c) for c in
        itertools.islice((colorsys.hsv_to_rgb(*x) for x in gethsvs()), n)]


def sequential_colors(n):
    """
    Between 3 and 9 sequential colors.
    """
    # https://personal.sron.nl/~pault/
    # as implemented by drmccloy here https://github.com/drammock/colorblind
    assert 3 <= n <= 9
    cols = ['#FFFFE5', '#FFFBD5', '#FFF7BC', '#FEE391', '#FED98E', '#FEC44F',
            '#FB9A29', '#EC7014', '#D95F0E', '#CC4C02', '#993404', '#8C2D04',
            '#662506']
    indices = [[2, 5, 8],
               [1, 3, 6, 9],
               [1, 3, 6, 8, 10],
               [1, 3, 5, 6, 8, 10],
               [1, 3, 5, 6, 7, 9, 10],
               [0, 2, 3, 5, 6, 7, 9, 10],
               [0, 2, 3, 5, 6, 7, 9, 10, 12]]
    return [cols[ix] for ix in indices[n - 3]]


def diverging_colors(n):
    """
    Between 3 and 11 diverging colors
    """
    # https://personal.sron.nl/~pault/
    # as implemented by drmccloy here https://github.com/drammock/colorblind
    assert 3 <= n <= 11
    cols = ['#3D52A1', '#3A89C9', '#008BCE', '#77B7E5', '#99C7EC', '#B4DDF7',
            '#E6F5FE', '#FFFAD2', '#FFE3AA', '#F9BD7E', '#F5A275', '#ED875E',
            '#D03232', '#D24D3E', '#AE1C3E']
    indices = [[4, 7, 10],
               [2, 5, 9, 12],
               [2, 5, 7, 9, 12],
               [1, 4, 6, 8, 10, 13],
               [1, 4, 6, 7, 8, 10, 13],
               [1, 3, 5, 6, 8, 9, 11, 13],
               [1, 3, 5, 6, 7, 8, 9, 11, 13],
               [0, 1, 3, 5, 6, 8, 9, 11, 13, 14],
               [0, 1, 3, 5, 6, 7, 8, 9, 11, 13, 14]]
    return [cols[ix] for ix in indices[n - 3]]
