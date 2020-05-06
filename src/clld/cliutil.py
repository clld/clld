"""Shared functionality for clld console scripts."""
import sys
import pathlib
import argparse
import warnings
import functools
import importlib
import collections

from distutils.util import strtobool
from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, bootstrap
from nameparser import HumanName
from clldutils.misc import slug

from clld.db.meta import DBSession, Base
from clld.db.models import common
from clld.lib import bibtex

__all__ = [
    'AppConfig',
    'BootstrappedAppConfig',
    'SessionContext',
    'data_file',
    'add_language_codes',
    'bibtex2source',
    'confirm',
    'Data']


class AppConfig(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        p = pathlib.Path(values.split('#')[0])
        if not (p.exists() and p.is_file()):
            raise ValueError()
        setattr(namespace, self.dest, p)
        namespace.module = p.resolve().parent.name
        namespace.settings = get_appsettings(values)

        if namespace.module == 'tests':
            namespace.module = 'clld'

        namespace.module = importlib.import_module(namespace.module)
        namespace.data_file = functools.partial(data_file, namespace.module)
        namespace.module_dir = pathlib.Path(namespace.module.__file__).parent
        namespace.migrations_dir = namespace.module_dir.joinpath('..', 'migrations')


class BootstrappedAppConfig(AppConfig):
    def __call__(self, parser, namespace, values, option_string=None):
        AppConfig.__call__(self, parser, namespace, values, option_string=option_string)
        namespace.env = bootstrap(values)
        try:
            namespace.initializedb = importlib.import_module(
                '.'.join([namespace.module.__name__, 'scripts', 'initializedb']))
        except ImportError as e:
            warnings.warn(str(e))
            namespace.initializedb = None


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
