"""Shared functionality for clld console scripts."""
import sys
import logging
import pathlib
import argparse
import functools
import collections

from distutils.util import strtobool
import transaction
from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging, bootstrap
from nameparser import HumanName
from clldutils.misc import slug
from clldutils.clilib import PathType

from clld.db.meta import DBSession, Base
from clld.db.models import common
from clld.lib import bibtex


class SessionContext:
    """
    To support accessing configured sessions in cli commands.
    """
    def __init__(self, settings):
        self.settings = {'sqlalchemy.url': settings} if isinstance(settings, str) else settings
        self.engine = None

    def __enter__(self):
        self.engine = engine_from_config(self.settings)
        DBSession.remove()
        DBSession.configure(bind=self.engine)
        assert DBSession.bind == self.engine
        Base.metadata.create_all(self.engine)
        return DBSession

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.engine:
            self.engine.dispose()
        DBSession.remove()


def get_env_and_settings(config_uri):
    return bootstrap(config_uri), get_appsettings(config_uri)


def add_language_codes(data, lang, isocode, glottocodes=None, glottocode=None):
    def identifier(type_, id_):
        return data.add(
            common.Identifier, '%s:%s' % (type_, id_),
            id='%s:%s' % (type_, id_),
            name=id_,
            type=getattr(common.IdentifierType, type_).value)

    if isocode and len(isocode) == 3:
        DBSession.add(common.LanguageIdentifier(
            language=lang, identifier=identifier('iso', isocode)))

    if glottocode or (glottocodes and isocode and isocode in glottocodes):
        glottocode = glottocode or glottocodes[isocode]
        DBSession.add(common.LanguageIdentifier(
            language=lang, identifier=identifier('glottolog', glottocode)))


def bibtex2source(rec, cls=common.Source, lowercase_id=False):
    year = bibtex.unescape(rec.get('year', 'nd'))
    fields = {}
    jsondata = {}
    for field in bibtex.FIELDS:
        if field in rec:
            value = bibtex.unescape(rec[field])
            container = fields if hasattr(cls, field) else jsondata
            container[field] = value

    etal = ''
    eds = ''
    authors = rec.get('author')
    if not authors:
        authors = rec.get('editor', '')
        if authors:
            eds = ' (eds.)'
    if authors:
        authors = bibtex.unescape(authors).split(' and ')
        if len(authors) > 2:
            authors = authors[:1]
            etal = ' et al.'

        authors = [HumanName(a) for a in authors]
        authors = [n.last or n.first for n in authors]
        authors = '%s%s%s' % (' and '.join(authors), etal, eds)

    return cls(
        id=slug(rec.id, lowercase=lowercase_id),
        name=('%s %s' % (authors, year)).strip(),
        description=bibtex.unescape(rec.get('title', rec.get('booktitle', ''))),
        jsondata=jsondata,
        bibtex_type=rec.genre,
        **fields)


def confirm(question, default=False):  # pragma: no cover
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    """
    while True:
        sys.stdout.write(question + (" [Y|n] " if default else " [y|N] "))
        choice = input().lower()
        if not choice:
            return default
        try:
            return strtobool(choice)
        except ValueError:
            sys.stdout.write(
                "Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def data_file(module, *comps):
    """Return Path object of file in the data directory of an app."""
    return pathlib.Path(module.__file__).parent.joinpath('..', 'data', *comps)


def setup_session(config_uri, engine=None):
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine or engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    return pathlib.Path(config_uri.split('#')[0]).resolve().parent.name


def augment_arguments(args, **kw):  # pragma: no cover
    """pass a truthy value as keyword parameter bootstrap to bootstrap the app."""
    engine = getattr(args, 'engine', kw.get('engine', None))
    args.env = bootstrap(str(args.config_uri)) if kw.get('bootstrap', False) else {}
    module = setup_session(str(args.config_uri), engine=engine)

    # make sure we create URLs in the correct domain
    if args.env:
        dataset = DBSession.query(common.Dataset).first()
        if dataset:
            args.env['request'].environ['HTTP_HOST'] = dataset.domain

    if module == 'tests':
        module = 'clld'
    args.module = __import__(args.module or module)
    args.log = logging.getLogger(args.module.__name__)
    if engine:
        args.log.info('using bind %s' % engine)
    args.data_file = functools.partial(data_file, args.module)
    args.module_dir = pathlib.Path(args.module.__file__).parent
    args.migrations_dir = pathlib.Path(args.module.__file__).parent.joinpath('..', 'migrations')
    return args


def parsed_args(*arg_specs, **kw):
    parser = argparse.ArgumentParser(description=kw.pop('description', None))
    parser.add_argument(
        "config_uri", type=PathType(type='file'), help="ini file providing app config")
    parser.add_argument("--module", default=None)
    for args, _kw in arg_specs:
        parser.add_argument(*args, **_kw)
    args = parser.parse_args(args=kw.pop('args', None))
    return augment_arguments(args)


def initializedb(*args, **kw):  # pragma: no cover
    create = kw.pop('create', None)
    prime_cache = kw.pop('prime_cache', None)
    args = list(args) + [(("--prime-cache-only",), dict(action="store_true"))]
    args = parsed_args(*args, **kw)
    if not args.prime_cache_only:
        if create:
            with transaction.manager:
                create(args)
    if prime_cache:
        with transaction.manager:
            prime_cache(args)


class Data(collections.defaultdict):

    """Dictionary, serving to store references to new db objects during data imports.

    The values are dictionaries, keyed by the name of the model class used to create the
    new objects.

    >>> data = Data()
    >>> l = data.add(common.Language, 'l', id='abc', name='Abc Language')
    >>> assert l == data['Language']['l']
    """

    def __init__(self, **kw):
        super(Data, self).__init__(dict)
        self.defaults = kw

    def add(self, model_, key_, **kw):
        """
        Create an instance of a model class to be persisted in the database.

        :param model_: The model class we want to create an instance of.
        :param key_: A key which can be used to retrieve the instance later.
        :param kw: Keyword parameters passed to model class for initialisation.
        :return: The newly created instance of model class.
        """
        if '.' in kw.get('id', ''):
            raise ValueError('Object id contains illegal character "."')
        if list(kw.keys()) == ['_obj']:
            # if a single keyword parameter _obj is passed, we take it to be the object
            # which should be added to the session.
            new = kw['_obj']
        else:
            for k, v in self.defaults.items():
                kw.setdefault(k, v)
            new = model_(**kw)
        self[model_.__name__][key_] = new
        DBSession.add(new)
        return new
