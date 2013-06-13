from collections import defaultdict

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging

from clld.db.meta import DBSession, Base


def setup_session(config_uri, session=None, base=None):
    session = session or DBSession
    base = base or Base
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    session.configure(bind=engine)
    base.metadata.create_all(engine)


class Data(defaultdict):
    """Dictionary, serving to store references to new db objects during data imports.

    The values are dictionaries, keyed by the name of the mapper class used to create the
    new objects.
    """
    def __init__(self):
        super(Data, self).__init__(dict)

    def add(self, model, key, **kw):
        if kw.keys() == ['_obj']:
            # if a single keyword parameter _obj is passed, we take it to be the object
            # which should be added to the session.
            new = kw['_obj']
        else:
            new = model(**kw)
        self[model.__mapper__.class_.__name__][key] = new
        DBSession.add(new)
        return new
