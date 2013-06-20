from collections import defaultdict
import argparse

from sqlalchemy import engine_from_config, create_engine
from path import path
from pyramid.paster import get_appsettings, setup_logging

from clld.db.meta import DBSession, Base


def setup_session(config_uri, session=None, base=None, engine=None):
    session = session or DBSession
    base = base or Base
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine or engine_from_config(settings, 'sqlalchemy.')
    session.configure(bind=engine)
    base.metadata.create_all(engine)


class ExistingConfig(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        path_ = path(values.split('#')[0])
        if not path_.exists():
            raise argparse.ArgumentError(values, 'file does not exist')
        setattr(namespace, self.dest, values)


def ArgumentParser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_uri", action=ExistingConfig, help="ini file providing app config")
    return parser


def initializedb(name, create=None, prime_cache=None, **kw):
    parser = ArgumentParser()
    #parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
    #                    help="increase output verbosity")
    parser.add_argument("--prime-cache-only", action="store_true")
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    engine = None
    if args.download:
        engine = create_engine('sqlite:///%s.sqlite' % name)
    setup_session(
        args.config_uri, session=kw.get('session'), base=kw.get('base'), engine=engine)
    if not args.prime_cache_only:
        if create:
            create()
    if prime_cache:
        prime_cache()


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
