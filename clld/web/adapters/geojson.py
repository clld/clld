from zope.interface import implementer, implementedBy
from pyramid.renderers import render as pyramid_render

from clld.web.adapters.base import Renderable
from clld import interfaces
from clld.util import flatten_dict


@implementer(interfaces.IRepresentation)
class GeoJson(Renderable):
    """Base class for adapters which render geojson feature collections.
    """
    extension = 'geojson'
    mimetype = 'application/geojson'
    send_mimetype = 'application/json'

    def featurecollection_properties(self, ctx, req):
        return {}  # pragma: no cover

    def feature_iterator(self, ctx, req):
        return iter([])  # pragma: no cover

    def feature_properties(self, ctx, req, feature):
        return {}  # pragma: no cover

    def feature_coordinates(self, ctx, req, feature):
        """
        :return: lonlat
        """
        return [0.0, 0.0]  # pragma: no cover

    def render(self, ctx, req, dump=True):
        features = []

        for feature in self.feature_iterator(ctx, req):
            properties = self.feature_properties(ctx, req, feature)
            if properties:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": self.feature_coordinates(ctx, req, feature)},
                    "properties": properties,
                })

        res = {
            'type': 'FeatureCollection',
            'properties': self.featurecollection_properties(ctx, req),
            'features': features,
        }
        return pyramid_render('json', res, request=req) if dump else res


class GeoJsonParameter(GeoJson):
    """Render a parameter's values as geojson feature collection.
    """
    def featurecollection_properties(self, ctx, req):
        return {'name': ctx.name}

    def feature_iterator(self, ctx, req):
        de = req.params.get('domainelement')
        if de:
            return [vs for vs in ctx.valuesets
                    if vs.values and vs.values[0].domainelement.id == de]
        return [vs for vs in ctx.valuesets if vs.values]

    def feature_coordinates(self, ctx, req, valueset):
        return [valueset.language.longitude, valueset.language.latitude]

    def feature_properties(self, ctx, req, valueset):
        marker = req.registry.queryUtility(interfaces.IMapMarker)
        _d = {'language': valueset.language.__json__(req)}
        if marker:
            _d['icon'] = marker(valueset, req)
        for i, v in enumerate(valueset.values):
            _d['values_%s' % i] = v.__json__(req)
        return flatten_dict(_d)


@implementer(interfaces.IIndex)
class GeoJsonLanguages(GeoJson):
    """Render a collection of languages as geojson feature collection.
    """
    def feature_iterator(self, ctx, req):
        return ctx.get_query(limit=5000)

    def feature_coordinates(self, ctx, req, feature):
        return [feature.longitude, feature.latitude]

    def feature_properties(self, ctx, req, feature):
        return flatten_dict({'language': feature.__json__(req)})
