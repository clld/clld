from __future__ import unicode_literals, print_function, division, absolute_import
from functools import partial

from six import PY2
from six.moves.configparser import ConfigParser
from clldutils.path import Path


def get_config(p):
    """Read a config file.

    :return: dict of ('section.option', value) pairs.
    """
    cfg = {}
    parser = ConfigParser()
    if hasattr(parser, 'read_file'):
        parser.read_file(Path(p).open(encoding='utf8'))
    else:  # pragma: no cover
        assert PY2
        # The `read_file` method is not available on ConfigParser in py2.7!
        parser.readfp(Path(p).open(encoding='utf8'))

    for section in parser.sections():
        getters = {
            'int': partial(parser.getint, section),
            'boolean': partial(parser.getboolean, section),
            'float': partial(parser.getfloat, section),
            'list': lambda option: parser.get(section, option).split(),
        }
        default = partial(parser.get, section)
        for option in parser.options(section):
            type_ = option.rpartition('_')[2] if '_' in option else None
            value = getters.get(type_, default)(option)
            cfg['{0}.{1}'.format(section, option)] = value

    return cfg
