"""Functionality to configure leaflet maps from python."""
from __future__ import unicode_literals, division, print_function, absolute_import
from six import string_types
from clldutils.misc import cached_property

from clld.interfaces import IDataTable, IMapMarker, IIcon
from clld.web.util import helpers
from clld.web.util.htmllib import HTML
from clld.web.util.component import Component
from clld.web.adapters.geojson import GeoJson, GeoJsonCombinationDomainElement, get_lonlat


class Layer(object):

    """Represents a layer in a leaflet map.

    A layer in our terminology is a
    `FeatureCollection <http://geojson.org/geojson-spec.html#feature-collection-objects>`_
    in geojson and a
    `geoJson layer <http://leafletjs.com/reference.html#geojson>`_
    in leaflet, i.e. a bunch of points on the map.
    """

    def __init__(self, id_, name, data, **kw):
        """Initialize a layer object.

        :param id_: Map-wide unique string identifying the layer.
        :param name: Human readable name of the layer.
        :param data: A GeoJSON FeatureCollection either specified as corresponding Python\
        dict or as URL which will serve the appropriate GeoJSON.
        :param kw: Additional keyword parameters are made available to the Layer as \
        instance attributes.
        """
        self.id = id_
        self.name = name
        self.data = data
        for k, v in kw.items():
            setattr(self, k, v)


class Legend(object):

    """Represents a navpill with a dropdown above a map."""

    def __init__(self,
                 map_,
                 name,
                 items,
                 label=None,
                 stay_open=False,
                 item_attrs=None,
                 pull_right=False):
        self.map = map_
        self.name = name
        self.label = label or name.capitalize()
        self.items = items
        self.stay_open = stay_open
        self.item_attrs = item_attrs or {}
        self.pull_right = pull_right

    def format_id(self, suffix=None):
        suffix = suffix or ''
        if suffix:
            suffix = '-' + suffix
        return 'legend-%s%s' % (self.name, suffix)

    def render_item(self, item):
        if not isinstance(item, (tuple, list)):
            item = [item]
        attrs = self.item_attrs
        if self.stay_open:
            class_ = attrs.get('class', attrs.get('class_', ''))
            attrs['class'] = class_ + ' stay-open'
        return HTML.li(*item, **attrs)

    def render(self):
        a_attrs = {
            'class': 'dropdown-toggle',
            'data-toggle': "dropdown",
            'href': "#",
            'id': self.format_id('opener')}
        ul_class = 'dropdown-menu'
        if self.stay_open:
            ul_class += ' stay-open'
        return HTML.li(
            HTML.a(self.label, HTML.b(class_='caret'), **a_attrs),
            HTML.ul(
                *map(self.render_item, self.items),
                **dict(class_=ul_class, id=self.format_id('container'))),
            class_='dropdown' + (' pull-right' if self.pull_right else ''),
            id=self.format_id(),
        )


class FilterLegend(Legend):

    """Legend with actionable items.

    Legend rendering radio controls to filter languages on a map in sync with a column
    of an associated DataTable.
    """

    def __init__(self, map_, value_getter, col=None, dt=None, **kw):
        """Initialize.

        @param value_getter: Name of a javascript object which will be called with the \
        properties associated with a map marker to determine its filter value.
        """
        kw.setdefault('stay_open', True)
        if col and dt:
            col = {c.name: c for c in dt.cols}.get(col)
        if col:
            kw.setdefault('label', col.js_args.get('sTitle'))
        Legend.__init__(self, map_, col.name if col else 'nocol', [], **kw)
        self.jsname = 'fl-' + self.name
        items = [self.li(col, '--any--', value_getter, checked=True)]
        for item in getattr(col, 'choices', []):
            items.append(self.li(col, item, value_getter))
        self.items = items

    def li_label(self, item):
        return item[1] if isinstance(item, (tuple, list)) else item

    def li(self, col, item, value_getter, checked=False):
        input_attrs = dict(
            type='radio',
            class_='stay-open %s inline' % self.jsname,
            name=self.jsname,
            value=item[0] if isinstance(item, (tuple, list)) else item,
            onclick=helpers.JS("CLLD.mapLegendFilter")(
                self.map.eid,
                self.name,
                self.jsname,
                helpers.JS(value_getter),
                col.dt.eid if col else None))
        if checked:
            input_attrs['checked'] = 'checked'
        return HTML.label(
            HTML.input(**input_attrs),
            ' ',
            self.li_label(item),
            class_="stay-open",
            style="margin-left:5px; margin-right:5px;",
        )


class Map(Component):

    """Represents the configuration for a leaflet map."""

    __template__ = 'clld:web/templates/map.mako'

    def __init__(self, ctx, req, eid='map'):
        """Initialize.

        :param ctx: context object of the current request.
        :param req: current pyramid request object.
        :param eid: Page-unique DOM-node ID.
        """
        self.req = req
        self.ctx = ctx
        self.eid = eid
        self.map_marker = req.registry.getUtility(IMapMarker)

    def get_options_from_req(self):
        params = self.req.params
        res = {}
        try:
            if 'lat' in params and 'lng' in params:
                res['center'] = list(map(float, [params['lat'], params['lng']]))
            if 'z' in params:
                res['zoom'] = int(params['z'])
        except (ValueError, TypeError):
            pass
        return res

    @cached_property()
    def layers(self):
        """The list of layers of the map.

        .. note:: Since layers may be costly to compute, we cache them per map instance.

        :return: list of :py:class:`clld.web.maps.Layer` instances.
        """
        return list(self.get_layers())

    def get_layers(self):
        """Generate the list of layers.

        :return: list or generator of :py:class:`clld.web.maps.Layer` instances.
        """
        route_params = {'ext': 'geojson'}
        if not IDataTable.providedBy(self.ctx):
            route_params['id'] = self.ctx.id
        route_name = self.req.matched_route.name
        if not route_name.endswith('_alt'):
            route_name += '_alt'
        yield Layer(
            getattr(self.ctx, 'id', 'id'),
            '%s' % self.ctx,
            self.req.route_url(route_name, **route_params))

    @cached_property()
    def legends(self):
        return list(self.get_legends())

    def get_legends(self):
        if len(self.layers) > 1:
            items = []
            total = 0
            repr_attrs = dict(class_='pull-right stay-open', style="padding-right: 10px;")

            for layer in self.layers:
                representation = ''
                if hasattr(layer, 'representation'):
                    total += layer.representation
                    representation = HTML.span(str(layer.representation), **repr_attrs)
                items.append([
                    HTML.label(
                        HTML.input(
                            class_="stay-open",
                            type="checkbox",
                            checked="checked",
                            onclick=helpers.JS_CLLD.mapToggleLayer(
                                self.eid, layer.id, helpers.JS("this"))),
                        getattr(layer, 'marker', ''),
                        layer.name,
                        class_="checkbox inline stay-open",
                        style="margin-left: 5px; margin-right: 5px;",
                    ),
                    representation,
                ])
            if total:
                items.append(HTML.span(HTML.b(str(total)), **repr_attrs))
            yield Legend(
                self,
                'layers',
                items,
                label='Legend',
                stay_open=True,
                item_attrs=dict(style='clear: right'))
        items = []
        for size in [15, 20, 30, 40]:
            attrs = dict(name="iconsize", value=str(size), type="radio")
            if size == self.options.get('icon_size', 30):
                attrs['checked'] = 'checked'
            items.append(HTML.label(
                HTML.input(onclick=helpers.JS_CLLD.mapResizeIcons(self.eid), **attrs),
                HTML.img(
                    height=str(size),
                    width=str(size),
                    src=self.req.registry.getUtility(IIcon, 'cff6600').url(self.req)),
                class_="radio",
                style="margin-left: 5px; margin-right: 5px;"))
        yield Legend(
            self,
            'iconsize',
            items,
            label='Icon size')

        def item(layer):
            return HTML.a(
                layer.name,
                onclick='return %s;' % helpers.JS_CLLD.mapShowGeojson(self.eid, layer.id),
                href=layer.data if isinstance(layer.data, string_types) else '#')
        yield Legend(
            self, 'geojson', map(item, self.layers), label='GeoJSON', pull_right=True)


class ParameterMap(Map):

    """Map displaying markers for valuesets associated with a parameter instance."""

    def get_layers(self):
        if self.ctx.domain:
            for de in self.ctx.domain:
                yield Layer(
                    de.id,
                    de.name,
                    self.req.resource_url(
                        self.ctx, ext='geojson',
                        _query=dict(domainelement=str(de.id), **self.req.query_params)
                    ),
                    marker=helpers.map_marker_img(self.req, de, marker=self.map_marker))
        else:
            yield Layer(
                self.ctx.id,
                self.ctx.name,
                self.req.resource_url(self.ctx, ext='geojson'))

    def get_default_options(self):
        return {'info_query': {'parameter': self.ctx.pk}, 'hash': True}


class GeoJsonMultiple(GeoJson):

    """Render a collection of languages as geojson feature collection."""

    def feature_iterator(self, ctx, req):
        return ctx

    def feature_properties(self, ctx, req, language):
        return {
            'icon': req.registry.getUtility(IIcon, 'tff0000').url(req),
            'icon_size': 10,
            'zindex': 1000}


class CombinationMap(Map):

    """Map for a combination of parameters."""

    def get_layers(self):
        for de in self.ctx.domain:
            if de.languages:
                yield Layer(
                    de.id,
                    de.name,
                    GeoJsonCombinationDomainElement(de).render(de, self.req, dump=False),
                    marker=HTML.img(src=de.icon.url(self.req), height='20', width='20'))
        if self.ctx.multiple:
            # yield another layer which can be used to mark languages with multiple
            # values, because this may not be visible when markers are stacked on top
            # of each other.
            icon_url = self.req.registry.getUtility(IIcon, 'tff0000').url(self.req)
            yield Layer(
                '__multiple__',
                'Languages with multiple values',
                GeoJsonMultiple(None).render(self.ctx.multiple, self.req, dump=False),
                marker=HTML.img(src=icon_url, height='20', width='20'))

    def get_options(self):
        return {'icon_size': 25, 'hash': True}


class LanguageMap(Map):

    """Map showing a single language."""

    def get_layers(self):
        yield Layer(
            self.ctx.id,
            self.ctx.name,
            GeoJson(self.ctx).render(self.ctx, self.req, dump=False))

    def get_default_options(self):
        return {
            'center': list(reversed(get_lonlat(self.ctx) or [0, 0])),
            'zoom': 3,
            'no_popup': True,
            'no_link': True,
            'sidebar': True}


class GeoJsonSelectedLanguages(GeoJson):

    """Represents the geo-data of an iterable selection of languages.

    The iterable is assumed to be passed into the adapter upon initialization.
    """

    def feature_iterator(self, ctx, req):
        return self.obj


class SelectedLanguagesMap(Map):

    """Map showing an arbitrary selection of languages."""

    def __init__(self, ctx, req, languages, geojson_impl=None, **kw):
        """Initialize.

        :param languages: Iterable collection of languages.
        :param geojson_impl: GeoJson implementation to use.
        """
        self.geojson_impl = geojson_impl or GeoJsonSelectedLanguages
        self.languages = languages
        Map.__init__(self, ctx, req, **kw)

    def get_options(self):
        return {'icon_size': 20, 'hash': True, 'show_labels': len(self.languages) < 100}

    def get_layers(self):
        yield Layer(
            'languages',
            'Languages',
            self.geojson_impl(self.languages).render(self.ctx, self.req, dump=False))


#
# The following code implements a map to overlay geojson for parameters from distinct
# datasets. It may be used by CrossGram at some point.
#
def layers(spec, size, zindex=0):  # pragma: no cover
    import requests

    app, pid, url = spec

    def normalize(geojson):
        for f in geojson['features']:
            f['properties']['icon_size'] = size
            f['properties']['zindex'] = zindex
            if f['geometry']['coordinates'][0] > 180:
                f['geometry']['coordinates'][0] = f['geometry']['coordinates'][0] - 360
        return geojson

    geojson = requests.get(url + '.geojson').json()
    id_ = '-'.join([app, pid])

    if geojson['properties']['domain'] and not geojson['features']:
        for de in geojson['properties']['domain']:
            yield Layer(
                '-'.join([id_, de['id']]),
                '%s: %s - %s' % (app, geojson['properties']['name'], de['name']),
                normalize(
                    requests.get(url + '.geojson?domainelement=' + de['id']).json()),
                size=size,
                link=url,
                marker=HTML.img(src=de['icon'], width=size, height=size))
    else:
        yield Layer(
            id_,
            '%s: %s' % (app, geojson['properties']['name']),
            normalize(geojson),
            size=size,
            link=url,
            domain=geojson['properties']['domain'])


class CombinedMap(Map):  # pragma: no cover

    """Map for combination of parameters from different clld apps."""

    def get_layers(self):
        for i, spec in enumerate(self.ctx):
            for layer in layers(spec, (i + 1) * 10 + 10, (i + 1) * (-1000)):
                yield layer

    def get_options(self):
        return {'no_popup': True, 'no_link': True}
