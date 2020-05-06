"""
Create the skeleton for a clld app project.

Variables:
- directory_name: The name of the project directory. This will also be used as name
  of the python package.
- cldf_module: If the app data is initialized from a CLDF dataset, specify the CLDF
  module this dataset conforms to (Wordlist|StructureDataset|Dictionary|Generic).
  Leave empty otherwise.
  Note that this requires passing an `--cldf` option to `clld initdb`.
- mpg: Specify "y" if the app is served from MPG servers, and thus needs to fulfill
  certain legal obligations (n|y).
"""
import pathlib

from clldutils.clilib import PathType
import clld

try:
    from cookiecutter.main import cookiecutter
    from cookiecutter.exceptions import OutputDirExistsException
except ImportError:  # pragma: no cover
    cookiecutter = None


def kv(string):
    k, v = string.split('=', maxsplit=1)
    return k, v


def register(parser):
    parser.add_argument(
        'outdir',
        type=PathType(must_exist=False, type='dir'),
        help="Output directory. The last path segment will be used as default value for the"
             "'directory_name' variable."
    )
    parser.add_argument(
        'variables',
        nargs='*',
        type=kv,
        help="If run non-interactively, defaults for the template variables can be passed in"
             "as 'key=value'-formatted arguments",
    )
    parser.add_argument(
        '-f', '--force',
        default=False,
        help="Overwrite an existing project directory",
        action='store_true',
    )
    parser.add_argument(
        '--quiet',
        default=False,
        help="Run non-interactively, i.e. do not prompt for template variable input.",
        action='store_true',
    )


def run(args):
    if not cookiecutter:  # pragma: no cover
        print('cookiecutter must be installed to create project templates')
        return 1

    extra = {'directory_name': str(args.outdir.name)}
    extra.update(dict(args.variables))
    try:
        cookiecutter(
            str(pathlib.Path(clld.__file__).parent / 'project_template'),
            output_dir=str(args.outdir.parent),
            extra_context=extra,
            overwrite_if_exists=args.force,
            no_input=args.quiet,
        )
    except OutputDirExistsException as e:
        print(e)
        print('Run with --force option to overwrite!')
        raise ValueError()
