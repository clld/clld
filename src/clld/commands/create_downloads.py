"""
Create downloads registered for a clld app.
"""
import argparse

from clldutils.clilib import PathType

from clld.interfaces import IDownload
from clld.scripts.util import augment_arguments


def register(parser):
    parser.add_argument(
        "config_uri", type=PathType(type='file'), help="ini file providing app config")
    parser.add_argument("--module", default=None, help=argparse.SUPPRESS)
    parser.add_argument(
        '-l', '--list', default=False, action='store_true', help='only list registered downloads')


def run(args):
    """
    Create all registered downloads (locally).
    """
    args = augment_arguments(args, bootstrap=True)
    for name, download in args.env['registry'].getUtilitiesFor(IDownload):
        args.log.info('creating download %s' % name)
        if not args.list:
            download.create(args.env['request'])  # pragma: no cover
