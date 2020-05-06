from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models import common
{% if cookiecutter.cldf_module %}
from clld_glottologfamily_plugin.models import HasFamilyMixin
{% endif %}

#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
{% if cookiecutter.cldf_module %}
@implementer(interfaces.ILanguage)
class Variety(CustomModelMixin, common.Language, HasFamilyMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    glottocode = Column(Unicode)
{% endif %}

{% if cookiecutter.cldf_module.lower() == 'wordlist' %}

@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, common.Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    concepticon_id = Column(Unicode)

{% elif cookiecutter.cldf_module.lower() == 'structuredataset' %}

@implementer(interfaces.IParameter)
class Feature(CustomModelMixin, common.Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)

{% endif %}