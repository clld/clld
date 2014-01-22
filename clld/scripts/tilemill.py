"""
jumpstart a tilemill project based on a dataset from a clld app.
"""
import sys
import os
from zipfile import ZipFile
import json
from urlparse import urlparse
from urllib import urlopen
from base64 import b64encode
from cgi import escape


def layer(project, param, url):
    """a layer description for the tilemill project file.
    """
    return {
        "geometry": "point",
        "extent": [-158, -33.866669, 178.08837900000003, 70.110481],
        "id": project,
        "class": "",
        "Datasource": {
            "file": url,
            "id": project,
            "project": project,
            "srs": ""
        },
        "srs-name": "autodetect",
        "srs": "",
        "advanced": {},
        "name": project,
    }


def project(name, param):
    """a tilemill project description, including a basic countries-of-the-world layer.
    """
    return {
        "bounds": [-180, -85.05112877980659, 180, 85.05112877980659],
        "center": [0, 0, 2],
        "format": "png",
        "interactivity": False,
        "minzoom": 0,
        "maxzoom": 22,
        "srs": "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 "
        "+y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over",
        "Stylesheet": ["style.mss"],
        "Layer": [
            {
                "id": "countries",
                "name": "countries",
                "srs": "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 "
                "+y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over",
                "geometry": "polygon",
                "Datasource": {
                    "file": "http://mapbox-geodata.s3.amazonaws.com/natural-earth-1.4.0/"
                    "cultural/10m-admin-0-countries.zip",
                    "type": "shape"
                }
            },
        ],
        "scale": 1,
        "metatile": 2,
        "name": name,
        "description": param['properties']['name'],
    }


def legend(param):
    """
    :return: HTML markup for a legend for a tilemill map project.

    .. note:: We include icons via data-uris.
    """
    def row(de):
        if de['icon']:
            src = 'data:image/png;base64,%s' % b64encode(urlopen(de['icon']).read())
            img = '<img src="%s" height="20" width="20" />' % src
        else:
            img = ''
        return '<tr><td>%s</td><td>%s</td></tr>' % (img, escape(de['name']))

    return '<table>%s</table>' % ''.join(map(row, param['properties']['domain']))


def style(project, param):
    """carto css styles for the features of one parameter.
    """
    def valueset(vs):
        icon = os.path.basename(urlparse(vs['properties']['icon']).path)
        return """\
    [language_id="%s"] {
        marker-file: url(icons/%s);
    }
""" % (vs['properties']['language']['id'], icon.replace('png', 'svg'))

    base_scale = 0.9
    scale = """\
    [zoom = 0] {
        marker-transform:"scale(%.1f)";
    }
    [zoom = 1] {
        marker-transform:"scale(%.1f)";
    }
    [zoom = 2] {
        marker-transform:"scale(%.1f)";
    }
    [zoom = 3] {
        marker-transform:"scale(%.1f)";
    }
    [zoom = 4] {
        marker-transform:"scale(%.1f)";
    }
    [zoom = 5] {
        marker-transform:"scale(%.1f)";
    }
    marker-transform:"scale(%.1f)";
""" % tuple([base_scale * 0.5] + [base_scale * (i / 10.0) for i in range(5, 11)])

    return """\
#%s {
    marker-allow-overlap: true;
%s
%s
}
""" % (project, scale, ''.join(map(valueset, param['features'])))


STYLE = """\
Map {
    background-color: #b8dee6;
}

#countries {
    ::outline {
        line-color: #85c5d3;
        line-width: 2;
        line-join: round;
    }
    polygon-fill: #fff;
}
"""


def main(url):
    """
    create zip archive including:
    - project.mml
    - style.mss
    - icons/
    """
    urlparts = urlparse(url)

    if not url.endswith('.geojson'):
        url += '.geojson'
    param = json.loads(urlopen(url).read())

    project_name = '%s-%s' % (
        urlparts.hostname.replace('.', '-'),
        os.path.splitext(os.path.basename(urlparts.path))[0])

    p = project(project_name, param)

    # note: for tilemill we use the geojson with flattened properties.
    p['Layer'].append(
        layer(project_name, param, url.replace('.geojson', '.flat.geojson')))
    p['legend'] = legend(param)
    p['interactivity'] = {
        "fields": [],
        "layer": project_name,
        "template_teaser": "{{{language_name}}}",
    }

    ppath = lambda *comps: os.path.join(project_name, *comps)
    with ZipFile('%s.zip' % project_name, 'w') as fp:
        fp.writestr(ppath('project.mml'), json.dumps(p))
        fp.writestr(ppath('style.mss'), '\n'.join([STYLE, style(project_name, param)]))

        for icon in set([f['properties']['icon'] for f in param['features']]):
            icon = icon.replace('.png', '.svg')
            fp.writestr(
                ppath('icons', os.path.basename(urlparse(icon).path)),
                urlopen(icon).read())


if __name__ == '__main__':  # pragma: no cover
    main(sys.argv[1])
