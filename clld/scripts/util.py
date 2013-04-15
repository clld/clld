from collections import defaultdict

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging

from clld.db.meta import DBSession, Base


def setup_session(config_uri):
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)


class Data(defaultdict):
    """Dictionary, serving to store references to new db objects during data imports.

    The values are dictionaries, keyed by the name of the mapper class used to create the
    new objects.
    """
    def __init__(self):
        super(Data, self).__init__(dict)

    def add(self, model, key, **kw):
        new = model(**kw)
        self[model.__mapper__.class_.__name__][key] = new
        DBSession.add(new)
        return new
