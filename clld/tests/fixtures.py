from sqlalchemy import Column, Integer, Unicode, ForeignKey

from clld.db.models import common
from clld.db.meta import CustomModelMixin


class CustomLanguage(CustomModelMixin, common.Language):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    custom = Column(Unicode)
