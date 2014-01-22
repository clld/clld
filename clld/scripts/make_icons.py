"""
script to create the default set of map marker icons distributed with clld.
"""
import sys

try:
    import pyx
    from pyx import bbox, unit, style, path, color, canvas, deco
    # set the scale to 1/20th of an inch
    unit.set(uscale=0.05, wscale=0.02, defaultunit="inch")

    linewidth = style.linewidth(1.2)
    #linewidth = style.linewidth(1.1)
except ImportError:  # pragma: no cover
    pyx = False

from pyramid.path import AssetResolver

from clld.web.icon import ICONS


def polygon(*points):  # pragma: no cover
    args = []
    for i, point in enumerate(points):
        args.append(path.moveto(*point) if i == 0 else path.lineto(*point))
    args.append(path.closepath())
    return path.path(*args)


shapes = {
    "c": path.circle(20, 20, 13.6),  # circle
    "s": path.rect(8, 8, 24, 24),  # square
    "t": polygon((2, 4), (38, 4), (20, 35)),  # triangle (pyramid)
    "f": polygon((2, 36), (38, 36), (20, 5)),  # inverted pyramid
    "d": polygon((20, 2), (38, 20), (20, 38), (2, 20)),  # diamond
}


def pyxColor(string):
    """
    :param string: RGB color name like 'ffffff'
    :return: pyx color.

    >>> assert pyxColor('ffffff')
    """
    assert len(string) == 6
    colorTuple = tuple(
        int('0x' + c, 16) for c in [string[i:i + 2] for i in range(0, 6, 2)])
    return color.rgb(*[i / 255.0 for i in colorTuple])


if __name__ == '__main__':  # pragma: no cover
    if not pyx:
        sys.exit(1)
    asset_resolver = AssetResolver()
    for icon in ICONS:
        c = canvas.canvas()
        c.draw(
            shapes[icon.name[0]],
            [deco.stroked([linewidth]), deco.filled([pyxColor(icon.name[1:])])])
        stream = c.pipeGS("pngalpha", resolution=20, bbox=bbox.bbox(0, 0, 40, 40))
        with open(asset_resolver.resolve(icon.asset_spec).abspath(), 'wb') as fp:
            fp.write(stream.read())
    sys.exit(0)
