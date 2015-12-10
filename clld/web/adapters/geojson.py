"""
Functionality to serialize clld objects as GeoJSON.

.. seealso:: http://geojson.org/
"""
from json import loads
from itertools import groupby

from zope.interface import implementer
from pyramid.renderers import render as pyramid_render
from sqlalchemy.orm import joinedload
from clldutils.misc import nfilter

from clld.web.adapters.base import Renderable
from clld import interfaces
from clld.db.meta import DBSession
from clld.db.models.common import ValueSet, Value, Language


_PACIFIC_CENTERED = False


def pacific_centered():
    global _PACIFIC_CENTERED
    _PACIFIC_CENTERED = True


def _flatten(d, parent_key=''):
    items = []

    if isinstance(d, list):
        for i, v in enumerate(d):
            items.extend(_flatten(v, '_'.join(filter(None, [parent_key, str(i)]))))
    elif isinstance(d, dict):
        for k, v in d.items():
            new_key = parent_key + '_' + k if parent_key else k
            items.extend(_flatten(v, new_key))
    else:
        items.append((parent_key, d))
    return items


def flatten(d):
    """tilemill can only handle flat properties objects.

    >>> sorted(flatten({'a': {'b': [1, {'c': 4}, 3]}}).keys())
    ['a_b_0', 'a_b_1_c', 'a_b_2']
    """
    return dict(_flatten(d))


def get_lonlat(obj):
    """
    Return coordinates of an object taking into account whether maps are pacific centered.

    Pacific centered means
    the world should be divided between Icelandic (westernmost language) and
    Tupi (easternmost language), i.e. between -17 and -36.

    We chose -26 as divider because that puts cape verde to the west of africa.

    .. seealso: https://github.com/Leaflet/Leaflet/issues/1360
    """
    if hasattr(obj, 'latitude') and hasattr(obj, 'longitude'):
        longitude, latitude = obj.longitude, obj.latitude
    elif isinstance(obj, (tuple, list)) and len(obj) == 2:
        longitude, latitude = obj
    else:
        return
    if longitude is None or latitude is None:
        return
    if _PACIFIC_CENTERED and longitude <= -26:
        longitude += 360
    return longitude, latitude


def get_feature(obj, lonlat=None, **properties):
    res = {
        'type': 'Feature',
        'properties': properties,
        'geometry': {'type': 'Point', 'coordinates': lonlat or get_lonlat(obj)}}
    if hasattr(obj, 'id'):
        res['id'] = obj.id
    if hasattr(obj, 'name'):
        res['properties'].setdefault('name', obj.name)
    return res


@implementer(interfaces.IRepresentation)
class GeoJson(Renderable):

    """Base class for adapters which render geojson feature collections.

    The geojson we serve to leaflet must fulfill the following requirements:
    - a layer member in the featurecollection properties.
    - an icon member in the feature properties.
    - a language.id member in feature properties.
    """

    name = "GeoJSON"
    extension = 'geojson'
    mimetype = 'application/geojson'
    send_mimetype = 'application/json'  # application/vnd.geo+json

    def _featurecollection_properties(self, ctx, req):
        """Get properties object for the FeatureCollection.

        We return the layer index passed in the request, to make sure the features are
        added to the correct layer group.
        """
        res = {'layer': req.params.get('layer', '')}
        res.update(self.featurecollection_properties(ctx, req))
        return res

    def featurecollection_properties(self, ctx, req):
        """override to add properties."""
        return {}

    def feature_iterator(self, ctx, req):
        """Yield objects which will be represented as GeoJSON features.

        Since the only objects we have geographic info about are Languages, we try to
        detect (collections of) Languages associated with ctx.

        :return: generator object.
        """
        if interfaces.IDataTable.providedBy(ctx) and ctx.model == Language:
            return ctx.get_query(limit=5000)
        if hasattr(ctx, 'languages'):
            return ctx.languages
        if interfaces.ILanguage.providedBy(ctx):
            return [ctx]
        return []

    def feature_properties(self, ctx, req, feature):
        """override to add properties."""
        return {}

    def get_language(self, ctx, req, feature):
        """override to fetch language object from non-default location."""
        return feature

    def get_features(self, ctx, req):
        map_marker = req.registry.getUtility(interfaces.IMapMarker)

        for feature in self.feature_iterator(ctx, req):
            language = self.get_language(ctx, req, feature)
            lonlat = get_lonlat(language)
            if lonlat:
                properties = self.feature_properties(ctx, req, feature) or {}
                properties.setdefault('icon', map_marker(feature, req))
                properties.setdefault('language', language)
                yield get_feature(language, lonlat=lonlat, **properties)

    def render(self, ctx, req, dump=True):
        res = {
            'type': 'FeatureCollection',
            'properties': self._featurecollection_properties(ctx, req),
            'features': list(self.get_features(ctx, req))}
        return pyramid_render('json', res, request=req) if dump else res


class GeoJsonParameter(GeoJson):

    """Render a parameter's values as geojson feature collection."""

    def featurecollection_properties(self, ctx, req):
        marker = req.registry.getUtility(interfaces.IMapMarker)
        return {
            'name': getattr(ctx, 'name', 'Values'),
            'domain': [
                {'icon': marker(de, req), 'id': de.id, 'name': de.name}
                for de in getattr(ctx, 'domain', [])]}

    def get_query(self, ctx, req):
        return DBSession.query(ValueSet)\
            .join(Value)\
            .filter(ValueSet.parameter_pk == ctx.pk)\
            .options(joinedload(ValueSet.values), joinedload(ValueSet.language))

    def feature_iterator(self, ctx, req):
        de = req.params.get('domainelement')
        if de:
            return [vs for vs in ctx.valuesets
                    if vs.values and vs.values[0].domainelement.id == de]
        return self.get_query(ctx, req)

    def get_language(self, ctx, req, valueset):
        return valueset.language

    def feature_properties(self, ctx, req, valueset):
        return {
            'values': list(valueset.values),
            'label': ', '.join(nfilter(v.name for v in valueset.values))
            or self.get_language(ctx, req, valueset).name}


class GeoJsonParameterMultipleValueSets(GeoJsonParameter):

    """GeoJSON adapter for parameters with multiple valuesets per language."""

    def feature_iterator(self, ctx, req):
        q = self.get_query(ctx, req)
        return groupby(q.order_by(ValueSet.language_pk), lambda vs: vs.language)

    def get_language(self, ctx, req, pair):
        return pair[0]

    def feature_properties(self, ctx, req, pair):
        return {}


class GeoJsonCombinationDomainElement(GeoJson):

    """GeoJSON adapter for a domain element of a combination of parameters."""

    def feature_properties(self, ctx, req, language):
        return {
            'icon': ctx.icon.url(req) if ctx.icon else '',
            'zindex': 1000 - len(ctx.languages)}


class GeoJsonParameterFlatProperties(GeoJsonParameter):

    """GeoJSON with flattened feature properties for importing in tilemill.

    .. seealso: https://github.com/mapbox/tilemill/issues/2294
    """

    name = "GeoJSON for tilemill"
    extension = 'flat.geojson'
    mimetype = 'application/flat+geojson'

    def render(self, ctx, req, dump=True):
        res = loads(GeoJson.render(self, ctx, req, dump=True))
        for f in res['features']:
            f['properties'] = flatten(f['properties'])
        return pyramid_render('json', res, request=req) if dump else res


@implementer(interfaces.IIndex)
class GeoJsonLanguages(GeoJson):
    """Render a collection of languages as geojson feature collection."""
