"""Provides functionality to create simple SVG pie charts."""
from __future__ import unicode_literals, division, absolute_import, print_function
from base64 import b64encode
import math
from xml.sax.saxutils import escape

from clld.lib.color import rgb_as_hex

__all__ = ['svg', 'data_url', 'icon', 'pie']


def svg(content, height=None, width=None):
    height = ' height="{0}"'.format(height) if height else ''
    width = ' width="{0}"'.format(width) if width else ''
    return """\
<svg  xmlns="http://www.w3.org/2000/svg"
      xmlns:xlink="http://www.w3.org/1999/xlink"{0}{1}>
  {2}
</svg>""".format(height, width, content)


def style(stroke=None, fill=None, stroke_width='1px', opacity=None):
    res = ''
    if fill:
        res += 'fill:{0};'.format(fill)
    if stroke:
        res += 'stroke:{0};stroke-width:{1};stroke-linecap:round;stroke-linejoin:round;'\
            .format(stroke, stroke_width)
    else:
        res += 'stroke:none;'
    if opacity:
        res += 'opacity:{0};'.format(opacity)
    return res


def data_url(svgxml):
    return "data:image/svg+xml;base64,{0}".format(
        b64encode(svgxml.encode('utf8')).decode())


def icon(spec, opacity=None):
    paths = {
        's': 'path d="M8 8 H32 V32 H8 V8"',
        'd': 'path d="M20 2 L38 20 L20 38 L2 20 L20 2"',
        'c': 'circle cx="20" cy="20" r="14"',
        'f': 'path d="M2 4 L38 4 L20 35 L2 4"',
        't': 'path d="M2 36 L38 36 L20 5 L2 36"',
    }
    elem = '<{0} style="{1}"/>'.format(
        paths[spec[0]], style(stroke='black', fill=rgb_as_hex(spec[1:]), opacity=opacity))
    return svg(elem, height=40, width=40)


def pie(data, colors, titles=None, width=34, stroke_circle=False):
    """Create SVG pie charts.

    :return: SVG representation of the data as pie chart.
    """
    cx = cy = round(width / 2, 1)
    radius = round((width - 2) / 2, 1)
    current_angle_rad = 0
    svg_content = []
    total = sum(data)
    titles = titles or [None] * len(data)
    stroke_circle = 'black' if stroke_circle is True else stroke_circle or 'none'

    def endpoint(angle_rad):
        """
        Calculate position of point on circle given an angle, a radius, and the location
        of the center of the circle Zero line points west.
        """
        return (round(cx - (radius * math.cos(angle_rad)), 1),
                round(cy - (radius * math.sin(angle_rad)), 1))

    if len(data) == 1:
        svg_content.append(
            '<circle cx="{0}" cy="{1}" r="{2}" style="stroke:{3}; fill:{4};">'.format(
                cx, cy, radius, stroke_circle, rgb_as_hex(colors[0])))
        if titles[0]:
            svg_content.append('<title>{0}</title>'.format(escape(titles[0])))
        svg_content.append('</circle>')
        return svg(''.join(svg_content), height=width, width=width)

    for angle_deg, color, title in zip([360.0 / total * d for d in data], colors, titles):
        radius1 = "M{0},{1} L{2},{3}".format(cx, cy, *endpoint(current_angle_rad))
        current_angle_rad += math.radians(angle_deg)
        arc = "A{0},{1} 0 {2},1 {3} {4}".format(
            radius, radius, 1 if angle_deg > 180 else 0, *endpoint(current_angle_rad))
        radius2 = "L%s,%s" % (cx, cy)
        svg_content.append(
            '<path d="{0} {1} {2}" style="{3}" transform="rotate(90 {4} {5})">'.format(
                radius1, arc, radius2, style(fill=rgb_as_hex(color)), cx, cy))
        if title:
            svg_content.append('<title>{0}</title>'.format(escape(title)))
        svg_content.append('</path>')

    if stroke_circle != 'none':
        svg_content.append(
            '<circle cx="%s" cy="%s" r="%s" style="stroke:%s; fill:none;"/>'
            % (cx, cy, radius, stroke_circle))

    return svg(''.join(svg_content), height=width, width=width)
