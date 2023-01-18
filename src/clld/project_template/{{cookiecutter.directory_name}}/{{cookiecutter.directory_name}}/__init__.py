import collections

from pyramid.config import Configurator
from clld.interfaces import IMapMarker, IValueSet, IValue, IDomainElement
from clld.web.icon import MapMarker
from clldutils.svg import pie, icon, data_url

# we must make sure custom models are known at database initialization!
from {{cookiecutter.directory_name}} import models


{% if cookiecutter.cldf_module.lower() == 'structuredataset' %}
class FeatureMapMarker(MapMarker):
    def __call__(self, ctx, req):
        if IValueSet.providedBy(ctx):
            c = collections.Counter([v.domainelement.jsondata['color'] for v in ctx.values])
            return data_url(pie(*list(zip(*[(v, k) for k, v in c.most_common()])), **dict(stroke_circle=True)))
        if IDomainElement.providedBy(ctx):
            return data_url(icon(ctx.jsondata['color'].replace('#', 'c')))
        if IValue.providedBy(ctx):
            return data_url(icon(ctx.domainelement.jsondata['color'].replace('#', 'c')))
        return super(FeatureMapMarker, self).__call__(ctx, req)
{% endif %}


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clld.web.app')
{% if cookiecutter.mpg == true %}
    config.include('clldmpg')
{% endif %}
{% if cookiecutter.cldf_module.lower() == 'structuredataset' %}
    config.registry.registerUtility(FeatureMapMarker(), IMapMarker)
{% endif %}
    return config.make_wsgi_app()
