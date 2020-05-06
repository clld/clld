"""
Create downloads registered for a clld app.
"""
from clld.interfaces import IDownload
from clld.cliutil import BootstrappedAppConfig


def register(parser):
    parser.add_argument(
        "config_uri", action=BootstrappedAppConfig, help="ini file providing app config")
    parser.add_argument(
        'domain',
        help="domain name under which the app is served. Necessary to create correct URLs "
             "in RDF downloads.",
    )
    parser.add_argument(
        '-l', '--list', default=False, action='store_true', help='only list registered downloads')


def run(args):
    """
    Create all registered downloads (locally).
    """
    if args.domain:
        args.env['request'].environ['HTTP_HOST'] = args.domain
    for name, download in args.env['registry'].getUtilitiesFor(IDownload):
        args.log.info('creating download %s' % name)
        if not args.list:
            download.create(args.env['request'])  # pragma: no cover
