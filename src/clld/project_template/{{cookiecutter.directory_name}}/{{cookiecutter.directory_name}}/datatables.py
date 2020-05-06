from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol
{% if cookiecutter.cldf_module %}
from clld_glottologfamily_plugin.models import Family
from clld_glottologfamily_plugin.datatables import FamilyCol
{% endif %}

from {{cookiecutter.directory_name}} import models


{% if cookiecutter.cldf_module %}

class Languages(datatables.Languages):
    def base_query(self, query):
        return query.join(Family).options(joinedload(models.Variety.family)).distinct()

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            FamilyCol(self, 'Family', models.Variety),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
            LinkToMapCol(self, 'm'),
        ]
{% endif %}


def includeme(config):
    """register custom datatables"""
{% if cookiecutter.cldf_module %}
    config.register_datatable('languages', Languages)
{% endif %}