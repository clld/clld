import sys

from pyx import bbox, unit, style, path, color, canvas, deco
from pyramid.path import AssetResolver

from clld.web.icon import ICONS

# set the scale to 1/20th of an inch
unit.set(uscale=0.05, wscale=0.02, defaultunit="inch")


#linewidth = style.linewidth(1.2)
linewidth = style.linewidth(1.0)


def polygon(*points):
    args = []
    for i, point in enumerate(points):
        args.append(path.moveto(*point) if i == 0 else path.lineto(*point))
    args.append(path.closepath())
    return path.path(*args)


shapes = {
    #"c": path.circle(10, 10, 7.6),  # circle
    #"s": path.rect(2.8, 2.8, 14.4, 14.4),  # square
    #"t": polygon((1, 2.5), (19, 2.5), (10, 18.5)),  # triangle (pyramid)
    #"f": polygon((1, 17.5), (19, 17.5), (10, 1.5)),  # inverted pyramid
    #"d": polygon((10, 1), (19, 10), (10, 19), (1, 10)),  # diamond
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
    """
    assert len(string) == 6
    colorTuple = tuple(int('0x' + c, 16) for c in [string[i:i+2] for i in range(0, 6, 2)])
    return color.rgb(*[i / 255.0 for i in colorTuple])


if __name__ == '__main__':
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
