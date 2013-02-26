from sqlalchemy import Column, Integer, Unicode, ForeignKey

from clld.db.models import common
from clld.db.versioned import Versioned
from clld.db.meta import CustomModelMixin


class CustomLanguage(common.Language, Versioned, CustomModelMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    custom = Column(Unicode)
