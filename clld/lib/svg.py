"""Provides functionality to create simple SVG pie charts."""
from __future__ import unicode_literals, division, absolute_import, print_function
import math
from operator import add

from six.moves import reduce


SVG_PIE_TEMPLATE = """\
<?xml version='1.0' encoding='utf-8'?>
<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" x="0px" y="0px"
     width="%(width)spx" height="%(width)spx" viewBox="0 0 %(width)s %(width)s"
     enable-background="new 0 0 %(width)s %(width)s">
%(paths)s
</svg>"""

SVG_PATH_TEMPLATE = '    <path fill="%s" d="%s" stroke="black" stroke-width="1" '\
                    'transform="translate(0.5, 0.5)"/>'
SVG_CIRCLE_TEMPLATE = '    <circle fill="%s" cx="%s" cy="%s" r="%s" stroke="black" '\
                      'stroke-width="1" transform="translate(0.5, 0.5)"/>'


def pie(data, colors, width=34):
    """Create SVG pie charts.

    :return: SVG representation of the data as pie chart.

    >>> assert pie([2, 7], ['eee', '111'])
    >>> assert pie([100], ['eee'])
    """
    radius = width / 2.0 - 0.5

    if len(data) == 1:
        paths = [SVG_CIRCLE_TEMPLATE % (colors[0], width / 2.0, width / 2.0, radius)]
    else:
        total = reduce(add, data)
        percent_scale = 100.0 / total
        prev_percent = 0
        rad_mult = 3.6 * (math.pi / 180)
        paths = []
        for index, value in enumerate(data):
            percent = percent_scale * value
            radians = (prev_percent + percent) * rad_mult
            path = ' '.join((
                "M%(radius)s,%(radius)s",
                "L%(x_start)s,%(y_start)s",
                "A%(radius)s,%(radius)s",
                "0,",
                "%(percent_greater_fifty)s,1,",
                "%(x_end)s %(y_end)s Z"))
            paths.append(SVG_PATH_TEMPLATE % (colors[index], path % dict(
                radius=radius,
                x_start=radius + (math.sin(radians) * radius),
                y_start=radius - (math.cos(radians) * radius),
                percent_greater_fifty=int(percent >= 50),
                x_end=radius + (math.sin(radians) * radius),
                y_end=radius - (math.cos(radians) * radius))))

            half_percent = prev_percent + percent / 2
            radians = half_percent * rad_mult

            prev_percent += percent

    return SVG_PIE_TEMPLATE % dict(width=width, paths='\n'.join(paths))
