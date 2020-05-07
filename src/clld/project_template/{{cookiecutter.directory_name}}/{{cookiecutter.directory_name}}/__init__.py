import collections

from pyramid.config import Configurator
{% if cookiecutter.cldf_module %}
from clld_glottologfamily_plugin import util
{% endif %}
from clld.interfaces import IMapMarker, IValueSet, IValue, IDomainElement
from clldutils.svg import pie, icon, data_url

# we must make sure custom models are known at database initialization!
from {{cookiecutter.directory_name}} import models


{% if cookiecutter.cldf_module %}
class LanguageByFamilyMapMarker(util.LanguageByFamilyMapMarker):
    def __call__(self, ctx, req):
    {% if cookiecutter.cldf_module.lower() == 'wordlist' %}
        if IValueSet.providedBy(ctx):
            if ctx.language.family:
                return data_url(icon(ctx.language.family.jsondata['icon']))
            return data_url(icon(req.registry.settings.get('clld.isolates_icon', util.ISOLATES_ICON)))
    {% elif cookiecutter.cldf_module.lower() == 'structuredataset' %}
        if IValueSet.providedBy(ctx):
            c = collections.Counter([v.domainelement.jsondata['color'] for v in ctx.values])
            return data_url(pie(*list(zip(*[(v, k) for k, v in c.most_common()])), **dict(stroke_circle=True)))
        if IDomainElement.providedBy(ctx):
            return data_url(icon(ctx.jsondata['color'].replace('#', 'c')))
        if IValue.providedBy(ctx):
            return data_url(icon(ctx.domainelement.jsondata['color'].replace('#', 'c')))
    {% endif %}
        return super(LanguageByFamilyMapMarker, self).__call__(ctx, req)
{% endif %}


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clld.web.app')
{% if cookiecutter.mpg %}
    config.include('clldmpg')
{% endif %}
{% if cookiecutter.cldf_module %}
    config.registry.registerUtility(LanguageByFamilyMapMarker(), IMapMarker)
{% endif %}
    return config.make_wsgi_app()
