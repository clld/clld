import sys
import string

from path import path as ospath

from pyx import *
from pyx import bbox

# set the scale to 1/20th of an inch
unit.set(uscale=0.05, wscale=0.02, defaultunit="inch")


linewidth = style.linewidth(1.2)

shapes = {"c": path.circle(10, 10, 7.6),
          "s": path.rect(2.8, 2.8, 14.4, 14.4),
          "t": path.path(path.moveto(1, 2.5),
                         path.lineto(19, 2.5),
                         path.lineto(10, 18.5),
                         path.closepath()),

          "f": path.path(path.moveto(1, 17.5),
                         path.lineto(19, 17.5),
                         path.lineto(10, 1.5),
                         path.closepath()),

          "d": path.path(path.moveto(10, 1),
                         path.lineto(19, 10),
                         path.lineto(10, 19),
                         path.lineto(1, 10),
                         path.closepath())}


def colors(level=3):
    """
            'A': {fillColor: '#fe3856'},
            'B': {fillColor: '#ed9c07'},
            'C': {fillColor: '#efe305'},
            'D': {fillColor: '#f3ffb0'},
            'X': {fillColor: '#e8e8e8'},
            '?': {fillColor: '#ffffff'}
    """
    return [
        (0xfe, 0x38, 0x56),
        (0xed, 0x9c, 0x7),
        (0xef, 0xe3, 0x5),
        (0xf3, 0xff, 0xb0),
        (0xe8, 0xe8, 0xe8),
        (0xff, 0xff, 0xff),
    ]
    return [(0, 0, 0),
            (0, 0, 13),
            (0, 9, 0),
            (6, 15, 3),
            (9, 0, 9),
            (9, 9, 15),
            (9, 15, 15),
            (10, 0, 0),
            (12, 12, 12),
            (13, 0, 0),
            (15, 4, 0),
            (15, 6, 0),
            (15, 6, 15),
            (15, 12, 0),
            (15, 15, 0),
            (15, 15, 12),
            (15, 15, 15)]


def colorName(colorTuple):
    return "".join(hex(i).split('x')[1].rjust(2, '0') for i in colorTuple)


def pyxColor(colorTuple):
    return color.rgb(*[i / 255.0 for i in colorTuple])
    #return color.rgb(*[i / 15.0 for i in colorTuple])


if __name__ == '__main__':
    output = ospath(sys.argv[1])
    for shapeName, shapePath in shapes.items():
        for colorTuple in colors(3):
            c = canvas.canvas()
            c.draw(
                shapePath,
                [deco.stroked([linewidth]), deco.filled([pyxColor(colorTuple)])])
            with open(output.joinpath("%s%s.png" % (shapeName, colorName(colorTuple))),
                      'wb') as fp:
                fp.write(c.pipeGS("pngalpha", resolution=20, bbox=bbox.bbox(0, 0, 20, 20)).read())

    #c = canvas.canvas()
    #c.pipeGS("trunk/wals/wals/static/images/icons/a000.png",
    #         device="pngalpha", resolution=20, bbox=bbox.bbox(0, 0, 20, 20))
