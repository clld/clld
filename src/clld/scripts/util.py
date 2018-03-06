"""Shared functionality for clld console scripts."""
from __future__ import unicode_literals, division, absolute_import, print_function
import sys
from distutils.util import strtobool
from collections import defaultdict
import argparse
import logging
from functools import partial

from six.moves.urllib.parse import quote_plus
from six.moves import input
import transaction
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy.orm import joinedload
from pyramid.paster import get_appsettings, setup_logging, bootstrap
import requests
from nameparser import HumanName
from clldutils.path import Path, as_posix, remove
from clldutils import jsonlib
from clldutils.misc import slug

from clld.db.meta import VersionedDBSession, DBSession, Base
from clld.db.models import common
from clld.db.util import page_query
from clld.lib import bibtex


def glottocodes_by_isocode(dburi, cols=['id']):
    """Query Glottolog.

    :dburi: If not None, sqlalchemy dburi for a glottolog database. If None, \
    glottolog.org will be queried.
    :cols: list of column/attribute names for which information should be gathered.
    :return: dict mapping iso639-3 codes to glottolog data.
    """
    glottocodes = {}
    if dburi:
        select = ', '.join('l.%s' % name for name in cols)
        glottolog = create_engine(dburi)
        for row in glottolog.execute(
            'select ll.hid, %s from language as l, languoid as ll where l.pk = ll.pk'
            % select
        ):
            if row[0]:
                glottocodes[row[0]] = row[1] if len(row) == 2 else row[1:]
    else:
        conv = defaultdict(lambda: lambda x: x, latitude=float, longitude=float)
        res = requests.get("http://glottolog.org/resourcemap.json?rsc=language")
        for rsc in res.json()['resources']:
            for id_ in rsc.get('identifiers', []):
                if id_['type'] == 'iso639-3':
                    row = [conv[col](rsc.get(col)) if rsc.get(col) is not None else None
                           for col in cols]
                    glottocodes[id_['identifier']] = row[0] if len(row) == 1 \
                        else tuple(row)
                    break
    return glottocodes


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
    return Path(module.__file__).parent.joinpath('..', 'data', *comps)


def setup_session(config_uri, engine=None):
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine or engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    VersionedDBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    return Path(config_uri.split('#')[0]).resolve().parent.name


class ExistingDir(argparse.Action):  # pragma: no cover

    """Action to select an existing directory."""

    def __call__(self, parser, namespace, values, option_string=None):
        path_ = Path(values)
        if not path_.exists():
            raise argparse.ArgumentError(self, 'path does not exist')
        if not path_.is_dir():
            raise argparse.ArgumentError(self, 'path is no directory')
        setattr(namespace, self.dest, path_)


class ExistingConfig(argparse.Action):  # pragma: no cover

    """Action to select an existing config file."""

    def __call__(self, parser, namespace, values, option_string=None):
        path_ = Path(values.split('#')[0])
        if not path_.exists():
            raise argparse.ArgumentError(self, 'file does not exist')
        setattr(namespace, self.dest, values)


class SqliteDb(argparse.Action):  # pragma: no cover

    """Action to select an sqlite db to connect to."""

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, 'engine', create_engine('sqlite:///%s' % values[0]))


def parsed_args(*arg_specs, **kw):  # pragma: no cover
    """pass a truthy value as keyword parameter bootstrap to bootstrap the app."""
    parser = argparse.ArgumentParser(description=kw.pop('description', None))
    parser.add_argument(
        "config_uri", action=ExistingConfig, help="ini file providing app config")
    parser.add_argument("--glottolog-dburi", default=None)
    parser.add_argument("--module", default=None)
    parser.add_argument(
        "--sqlite", nargs=1, action=SqliteDb, help="sqlite db file")
    for args, _kw in arg_specs:
        parser.add_argument(*args, **_kw)
    args = parser.parse_args(args=kw.pop('args', None))
    engine = getattr(args, 'engine', kw.get('engine', None))
    args.env = bootstrap(args.config_uri) if kw.get('bootstrap', False) else {}
    module = setup_session(args.config_uri, engine=engine)

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
    args.data_file = partial(data_file, args.module)
    args.module_dir = Path(args.module.__file__).parent
    args.migrations_dir = Path(args.module.__file__).parent.joinpath('..', 'migrations')
    return args


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


def gbs_func(command, args, sources=None):  # pragma: no cover
    def words(s):
        return set(slug(s.strip(), remove_whitespace=False).split())

    log = args.log
    count = 0
    api_url = "https://www.googleapis.com/books/v1/volumes?"

    if command == 'cleanup':
        for fname in args.data_file('gbs').glob('*.json'):
            try:
                data = jsonlib.load(fname)
                if data.get('totalItems') == 0:
                    remove(fname)
            except ValueError:
                remove(fname)
        return

    if not sources:
        sources = DBSession.query(common.Source)\
            .order_by(common.Source.id)\
            .options(joinedload(common.Source.data))
    if callable(sources):
        sources = sources()

    for i, source in enumerate(page_query(sources, verbose=True, commit=True)):
        filepath = args.data_file('gbs', 'source%s.json' % source.id)

        if command == 'update':
            source.google_book_search_id = None
            source.update_jsondata(gbs={})

        if command in ['verify', 'update']:
            if filepath.exists():
                try:
                    data = jsonlib.load(filepath)
                except ValueError:
                    log.warn('no JSON object found in: %s' % filepath)
                    continue
                if not data['totalItems']:
                    continue
                item = data['items'][0]
            else:
                continue

        if command == 'verify':
            stitle = source.description or source.title or source.booktitle
            needs_check = False
            year = item['volumeInfo'].get('publishedDate', '').split('-')[0]
            if not year or year != slug(source.year or ''):
                needs_check = True
            twords = words(stitle)
            iwords = words(
                item['volumeInfo']['title'] + ' '
                + item['volumeInfo'].get('subtitle', ''))
            if twords == iwords \
                    or (len(iwords) > 2 and iwords.issubset(twords))\
                    or (len(twords) > 2 and twords.issubset(iwords)):
                needs_check = False
            if int(source.id) == 241:
                log.info('%s' % sorted(words(stitle)))
                log.info('%s' % sorted(iwords))
            if needs_check:
                log.info('------- %s -> %s' % (
                    source.id, item['volumeInfo'].get('industryIdentifiers')))
                log.info('%s %s' % (
                    item['volumeInfo']['title'], item['volumeInfo'].get('subtitle', '')))
                log.info(stitle)
                log.info(item['volumeInfo'].get('publishedDate'))
                log.info(source.year)
                log.info(item['volumeInfo'].get('authors'))
                log.info(source.author)
                log.info(item['volumeInfo'].get('publisher'))
                log.info(source.publisher)
                if not confirm('Are the records the same?'):
                    log.warn('---- removing ----')
                    jsonlib.dump({"totalItems": 0}, filepath)
        elif command == 'update':
            source.google_book_search_id = item['id']
            source.update_jsondata(gbs=item)
            count += 1
        elif command == 'download':
            if source.author and (source.title or source.booktitle):
                title = source.title or source.booktitle
                if filepath.exists():
                    continue
                q = [
                    'inauthor:' + quote_plus(source.author.encode('utf8')),
                    'intitle:' + quote_plus(title.encode('utf8')),
                ]
                if source.publisher:
                    q.append('inpublisher:' + quote_plus(
                        source.publisher.encode('utf8')))
                url = api_url + 'q=%s&key=%s' % ('+'.join(q), args.api_key)
                count += 1
                r = requests.get(url, headers={'accept': 'application/json'})
                log.info('%s - %s' % (r.status_code, url))
                if r.status_code == 200:
                    with open(as_posix(filepath), 'w') as fp:
                        fp.write(r.text.encode('utf8'))
                elif r.status_code == 403:
                    log.warn("limit reached")
                    break
    if command == 'update':
        log.info('assigned gbs ids for %s out of %s sources' % (count, i))
    elif command == 'download':
        log.info('queried gbs for %s sources' % count)


class Data(defaultdict):

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

    def add(self, model, key, **kw):
        """
        Create an instance of a model class to be persisted in the database.

        :param model: The model class we want to create an instance of.
        :param key: A key which can be used to retrieve the instance later.
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
            new = model(**kw)
        self[model.__name__][key] = new
        DBSession.add(new)
        return new
