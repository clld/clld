from pyramid.config import Configurator
{% if cookiecutter.cldf_module %}
from clld_glottologfamily_plugin import util
{% endif %}
from clld.interfaces import IMapMarker, IValueSet

# we must make sure custom models are known at database initialization!
from {{cookiecutter.directory_name}} import models


{% if cookiecutter.cldf_module %}
class LanguageByFamilyMapMarker(util.LanguageByFamilyMapMarker):
    def get_icon(self, ctx, req):
        if IValueSet.providedBy(ctx):
            if ctx.language.family:
                return ctx.language.family.jsondata['icon']
            return req.registry.settings.get('clld.isolates_icon', util.ISOLATES_ICON)
        return super(LanguageByFamilyMapMarker, self).get_icon(ctx, req)
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
