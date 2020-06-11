"""

"""
import pathlib
import contextlib

import transaction
from clldutils import db
from clldutils.clilib import PathType
from clld.cliutil import SessionContext, BootstrappedAppConfig
from pycldf import Dataset

try:
    from cldfcatalog import Catalog
except ImportError:  # pragma: no cover
    Catalog = None


def register(parser):
    parser.add_argument(
        "config-uri",
        action=BootstrappedAppConfig,
        help="ini file providing app config",
    )
    parser.add_argument(
        '--prime-cache-only',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--cldf',
        type=PathType(type='file'),
        default=None,
    )
    for name in ['concepticon', 'glottolog']:
        parser.add_argument(
            '--' + name,
            metavar=name.upper(),
            help='Path to repository clone of {0} data'.format(name.capitalize()),
            default=None)
        parser.add_argument(
            '--{0}-version'.format(name),
            help='Version of {0} data to checkout'.format(name.capitalize()),
            default=None)


def run(args):
    if (args.glottolog or args.concepticon) and Catalog is None:  # pragma: no cover
        print('To use reference catalogs you must install the cldfcatalog package!')
        return 10

    if args.cldf:  # pragma: no cover
        args.cldf = Dataset.from_metadata(args.cldf)

    with contextlib.ExitStack() as stack:
        if not args.prime_cache_only:
            stack.enter_context(db.FreshDB.from_settings(args.settings, log=args.log))
        stack.enter_context(SessionContext(args.settings))

        for name in ['concepticon', 'glottolog']:
            if getattr(args, name):  # pragma: no cover
                if getattr(args, name + '_version'):
                    stack.enter_context(
                        Catalog(getattr(args, name), tag=getattr(args, name + '_version')))
                else:
                    setattr(args, name, pathlib.Path(getattr(args, name)))

        if not args.prime_cache_only:
            with transaction.manager:
                if args.initializedb:  # pragma: no cover
                    args.initializedb.main(args)
        if hasattr(args.initializedb, 'prime_cache'):
            with transaction.manager:  # pragma: no cover
                args.initializedb.prime_cache(args)
