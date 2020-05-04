"""
Functionality to be called from command line scripts is provided in this module.

.. note:

    The various scripts are installed when running `python setup.py develop|install`,
    following the specification in `setup.py`.

.. seealso: http://www.scotttorborg.com/python-packaging/command-line-scripts.html\
#the-console-scripts-entry-point
"""
from clld.interfaces import IDownload
from clld.scripts.util import parsed_args


def create_downloads(**kw):  # pragma: no cover
    """
    Create all registered downloads (locally).
    """
    args = parsed_args(bootstrap=True, description=create_downloads.__doc__)
    for name, download in args.env['registry'].getUtilitiesFor(IDownload):
        args.log.info('creating download %s' % name)
        download.create(args.env['request'])
